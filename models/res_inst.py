from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg, Value, Sum, Count
from django.db.models.functions import Coalesce

from res_type import Resource_Type

class Unit(models.Model):
    shortcode       = models.CharField(max_length=8)
    verbose_name    = models.CharField(max_length=20)
    verbose_plural  = models.CharField(max_length=20)

    def __str__(self):
        return "%s (%s)" % (self.verbose_plural, self.shortcode)

class Resource_Inst(models.Model):
    res_name        = models.CharField(max_length=40)
    res_type        = models.ForeignKey(Resource_Type)
    price           = models.IntegerField()
    unit_use_formal = models.BooleanField(default=False)
    orig_unit       = models.ForeignKey(Unit)
    amt_original    = models.FloatField()
    used_so_far     = models.FloatField(default=0)
    best_bef_date   = models.DateTimeField("best before date")
    best_before     = models.BooleanField(default=True)
    purchase_date   = models.DateTimeField("purchase date")
    exhausted       = models.BooleanField(default=False)
    inst_owner      = models.ForeignKey(User)
    last_mod        = models.DateTimeField(auto_now=True)

    def finalise(self):
        self.set_finalisation(True)

    def definalise(self):
        self.set_finalisation(False)

    def set_finalisation(self, finalisation):
        assert isinstance(finalisation, bool), "Invalid finalisation"
        #   We need to find all the tickets and update them
        self.exhausted = finalisation
        affected_tickets = self.resource_ticket_set.all()
        for ticket in affected_tickets:
            if finalisation:
                ticket.finalise()
            else:
                ticket.definalise()
        self.save()
        return

    def update_usage(self, added_units):
        assert added_units < 0 or not self.exhausted, \
            "Unable to use an exhausted resource"
        if added_units == 0:
            return
        #   We want to:
        #   1. Check the current (units) usage of the resource `inst`
        #   2. Update the usage, taking the fraction of the added usage to
        #       produce the cost of the increment
        #   3. Check Resource_Ticket instances for references to `inst`, and
        #       amortise their respective `ticket_cost`s
        self.used_so_far += added_units
        self.refresh_dependent_ticket_prices()
        self.save()
        return self.price * added_units / self.used_so_far \
                    if self.used_so_far != 0 else 0

    def change_name(self, newName):
        self.res_name = newName
        self.save()

    def change_type(self, newType):
        self.res_type = newType
        self.save()

    def change_price(self, newPrice):
        self.price = newPrice
        self.refresh_dependent_ticket_prices()
        self.save()

    def change_amt(self, newAmt):
        self.amt_original = newAmt
        print "%f %d" % (newAmt, self.id)
        self.save()

    def refresh_dependent_ticket_prices(self):
        was_finalised = self.exhausted
        self.definalise()

        affected_tickets = self.resource_ticket_set.all()
        for ticket in affected_tickets:
            ticket.updatePrice(
                self.price * ticket.used_on_ticket / self.used_so_far)

        self.set_finalisation(was_finalised)

    def similar_set(self, user):
        return Resource_Inst.objects.filter(res_name__iexact=self.res_name,
                        inst_owner=user).order_by('purchase_date', 'id')

    def similar_attrs(self, user):
        return self.similar_set(user).filter(exhausted=True).aggregate(
                        tot_usage=Coalesce(Sum('used_so_far'), Value(0)),
                        tot_cost=Coalesce(Sum('price'), Value(0)),
                        tot_vol=Coalesce(Sum('amt_original'), Value(0)),
                        ct=Count('id'), )

    def single_unit_vol(self, user):
        att = self.similar_attrs(user)
        return 0 if att['tot_usage'] == 0 else att['tot_vol'] / att['tot_usage']

    def __str__(self):
        return self.res_name + " (" + str(self.id) + ")"

    class Meta:
        verbose_name        = "resource instance"
