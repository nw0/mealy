from django.db import models
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User

from .meal import Meal

class Dish(models.Model):
    COOKING_STYLES = (
        ('frying',      "Fried"),
        ('boiling',     "Boiled"),
        ('baking',      "Baked"),
        ('roasting',    "Roasted"),
        ('uncooked',    "Processed"),
        ('instant',     "Microwaved")
    )
    cooking_style   = models.CharField(max_length=8, choices=COOKING_STYLES)
    par_meal        = models.ForeignKey(Meal)
    ticket_deps     = models.IntegerField(default=0)

    def updatePriceDelta(self, delta):
        assert self.ticket_deps > 0, "Dish has no open tickets"
        self.par_meal.openCostsDelta(delta)

    def remove_ticket(self, ticket_cost):
        assert self.ticket_deps > 0, "Dish has no open tickets"
        self.updatePriceDelta(-ticket_cost)
        self.ticket_deps -= 1
        self.save()

    def add_dep(self, dep_cost):
        self.ticket_deps += 1
        self.save()

        self.updatePriceDelta(dep_cost)

    def close_dep(self, dep_cost):
        #   Assume that closure will always involve a positive cost
        #   Then: if dep_cost < 0, this signifies a "re-opening" of costs
        if dep_cost >= 0:
            assert self.ticket_deps > 0, "Dish has no open tickets"
            self.ticket_deps -= 1
        else:
            self.ticket_deps += 1

        self.save()
        self.par_meal.close_cost(dep_cost)

    def get_closed_cost(self):
        tickets = self.resource_ticket_set.filter(finalised=True)
        return tickets.aggregate(c=Coalesce(Sum('ticket_cost'), Value(0)))['c']

    def get_open_cost(self):
        tickets = self.resource_ticket_set.filter(finalised=False)
        return tickets.aggregate(c=Coalesce(Sum('ticket_cost'), Value(0)))['c']

    def refreshDeps(self):
        self.ticket_deps \
            = self.resource_ticket_set.filter(finalised=False).count()
        self.save()

    def __str__(self):
        tickets = self.resource_ticket_set.all().order_by('-ticket_cost')
        if tickets.distinct().count() == 0:
            return "%s (empty)" % self.cooking_style
        return "%s %s" % (self.get_cooking_style_display(), tickets[0])

    class Meta:
        verbose_name_plural = "dishes"
