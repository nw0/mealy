from django.db import models
from django.contrib.auth.models import User

class Meal(models.Model):
    MEAL_TYPES = (
        ("Breakfast",   "Breakfast"),
        ("Lunch",       "Lunch"),
        ("Dinner",      "Dinner"),
        ("Tea",         "Tea"),
        ("Supper",      "Supper"),
        ("Snack",       "Snack")
    )
    cons_time   = models.DateTimeField("time eaten")
    meal_type   = models.CharField(choices=MEAL_TYPES, max_length=10)
    open_cost   = models.FloatField(default=0)
    closed_cost = models.FloatField(default=0)
    dish_deps   = models.IntegerField(default=0)
    meal_owner  = models.ForeignKey(User)

    def updatePriceDelta(self, delta):
        self.open_cost += delta
        self.save()

    def refreshCosts(self):
        dishes = self.dish_set.filter(par_meal=self)
        self.open_cost = sum([ dish.get_open_cost() for dish in dishes ])
        self.closed_cost = sum([ dish.get_closed_cost() for dish in dishes ])
        self.save()

    def add_dep(self):
        self.dish_deps += 1
        self.save()

    def close_dep(self):
        self.dish_deps -= 1
        self.save()

    def get_meal_cost(self):
        return (self.open_cost + self.closed_cost)

    def close_cost(self, dep_cost):
        #   Assume that closure will always involve shifting a positive cost
        #    from open_cost to closed_cost
        #   Then: if dep_cost < 0, this signifies a "re-opening" of costs
        self.open_cost -= dep_cost
        self.closed_cost += dep_cost
        self.save()

    def __str__(self):
        return self.meal_type + " on " + self.cons_time.strftime("%B %-d, %Y")
