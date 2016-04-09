from django.db import models
from django.contrib.auth.models import User

from res_type import Resource_Type

class Resource_Inst(models.Model):
    res_name        = models.CharField(max_length=40)
    res_type        = models.ForeignKey(Resource_Type)
    unit_use_formal = models.BooleanField(default=False)
    units_original  = models.CharField(max_length=6)
    amt_original    = models.IntegerField()
    price           = models.IntegerField()
    used_so_far     = models.FloatField(default=0)
    best_before     = models.BooleanField(default=False)
    best_bef_date   = models.DateTimeField("best before date")
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

    def update_usage(self, added_units, is_exhausted):
        assert added_units < 0 or not self.exhausted, \
            "Unable to use an exhausted resource"
        if added_units == 0:
            return
        if not isinstance(is_exhausted, bool):
            is_exhausted = self.exhausted
        #   We want to:
        #   1. Check the current (units) usage of the resource `inst`
        #   2. Update the usage, taking the fraction of the added usage to
        #       produce the cost of the increment
        #   3. Check Resource_Ticket instances for references to `inst`, and
        #       amortise their respective `ticket_cost`s
        self.used_so_far += added_units
        self.refresh_dependent_ticket_prices()
        self.save()
        if is_exhausted:
            self.finalise()
        return self.price * added_units / self.used_so_far

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

    def refresh_dependent_ticket_prices(self):
        was_finalised = self.exhausted
        self.definalise()

        affected_tickets = self.resource_ticket_set.all()
        for ticket in affected_tickets:
            ticket.updatePrice(
                self.price * ticket.used_on_ticket / self.used_so_far)

        self.set_finalisation(was_finalised)

    def __str__(self):
        return self.res_name + " (" + str(self.id) + ")"
