from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models import signals

from res_inst import Resource_Inst
from dish import Dish

class TicketManager(models.Manager):
    def create_ticket(self, resource_inst, used_on_ticket, dish,
        resource_exhausted=False):
        #   Reject the ticket if used is 0
        if used_on_ticket <= 0:
            return False
        ticket = self.create(
            resource_inst   = resource_inst,
            used_on_ticket  = used_on_ticket,
            ticket_cost     = resource_inst.update_usage(used_on_ticket),
            par_dish        = dish
        )
        ticket.save()
        ticket.par_dish.add_dep(ticket.ticket_cost)
        if resource_exhausted:
            resource_inst.finalise()
        return ticket

class Resource_Ticket(models.Model):
    resource_inst   = models.ForeignKey(Resource_Inst)
    used_on_ticket  = models.FloatField()
    ticket_cost     = models.FloatField()
    finalised       = models.BooleanField(default=False)
    par_dish        = models.ForeignKey(Dish)

    objects = TicketManager()

    def updatePrice(self, newPrice):
        assert not self.finalised, "Ticket has been finalised"
        #   We need to find all the dishes and update the price
        delta = newPrice - self.ticket_cost
        self.ticket_cost = newPrice
        self.save()
        self.par_dish.updatePriceDelta(delta)

    def finalise(self):
        #   Do not call this method except through Resource_Inst.finalise()
        #   We need to find the meal and see if it can be finalised
        if not self.finalised:
            self.finalised = True
            self.save()
            self.par_dish.close_dep(self.ticket_cost)

    def definalise(self):
        if self.finalised:
            self.finalised = False
            self.save()
            self.par_dish.close_dep(-self.ticket_cost)

    def __str__(self):
        return self.resource_inst.res_name

    class Meta:
        verbose_name    = "resource ticket"

@receiver(signals.post_delete, sender=Resource_Ticket)
def clean_ticket(sender, **kwargs):
    ticket = kwargs.get('instance')
    was_finalised = ticket.finalised

    if was_finalised:
        ticket.resource_inst.definalise()
        ticket.par_dish.close_dep(-ticket.ticket_cost)

    ticket.par_dish.remove_ticket(ticket.ticket_cost)
    ticket.resource_inst.update_usage(-ticket.used_on_ticket)

    if was_finalised:
        ticket.resource_inst.finalise()
