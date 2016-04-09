from django.db import models
from django.contrib.auth.models import User

from meal import Meal

class Dish(models.Model):
    COOKING_STYLES = (
        ('frying',      "Fried"),
        ('boiling',     "Boiled"),
        ('baking',      "Baked"),
        ('roasting',    "Roasted"),
        ('instant',     "Microwaved")
    )
    cooking_style   = models.CharField(max_length=8, choices=COOKING_STYLES)
    par_meal        = models.ForeignKey(Meal)
    ticket_deps     = models.IntegerField(default=0)

    def updatePriceDelta(self, delta):
        #   Add the delta to the meal price
        self.par_meal.updatePriceDelta(delta)

    def remove_ticket(self, ticket_cost):
        #   Assumes the ticket is open
        self.ticket_deps -= 1
        self.save()

        self.par_meal.updatePriceDelta(-ticket_cost)
        if self.ticket_deps <= 0:
            self.par_meal.close_dep()

    def add_dep(self, dep_cost):
        self.ticket_deps += 1
        self.save()

        self.par_meal.updatePriceDelta(dep_cost)
        if self.ticket_deps == 1:
            self.par_meal.add_dep()

    def reopen_dep(self, dep_cost):
        self.ticket_deps += 1
        self.save()

        self.par_meal.reopen_cost(dep_cost)
        if self.ticket_deps == 1:
            self.par_meal.add_dep()

    def close_dep(self, dep_cost):
        self.ticket_deps -= 1
        self.save()
        self.par_meal.close_cost(dep_cost)

        if self.ticket_deps <= 0:
            self.par_meal.close_dep()

    def get_closed_cost(self):
        tickets = self.resource_ticket_set.filter(par_dish=self, finalised=True)
        return sum([ ticket.ticket_cost for ticket in tickets ])

    def get_open_cost(self):
        tickets = self.resource_ticket_set.filter(par_dish=self, finalised=False)
        return sum([ ticket.ticket_cost for ticket in tickets ])

    def __str__(self):
        tickets = self.resource_ticket_set.filter(par_dish=self).order_by('id')
        tCount = tickets.distinct().count()
        if tCount == 0:
            return "%s (empty)" % self.cooking_style
        return "%s %s" % (self.get_cooking_style_display(), tickets[0])
