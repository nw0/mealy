from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Resource_Type(models.Model):
    r_parent    = models.ForeignKey('self', default=None, null=True)
    r_name      = models.CharField(max_length=40)

    def __str__(self):
        return self.r_name

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
        #   We need to find all the tickets and update them
        self.exhausted = True
        affected_tickets = Resource_Ticket.objects.filter(resource_inst=self)
        for ticket in affected_tickets:
            ticket.finalise()
        self.save()
        return

    def update_usage(self, added_units, is_exhausted):
        if added_units <= 0:
            return 0
        #   We want to:
        #   1. Check the current (units) usage of the resource `inst`
        #   2. Update the usage, taking the fraction of the added usage to
        #       produce the cost of the increment
        #   3. Check Resource_Ticket instances for references to `inst`, and
        #       amortise their respective `ticket_cost`s
        self.used_so_far += added_units
        if self.used_so_far == added_units:
            self.save()
            return self.price
        affected_tickets = Resource_Ticket.objects.filter(resource_inst=self)
        for ticket in affected_tickets:
            ticket.updatePrice(
                self.price * ticket.used_on_ticket / self.used_so_far)
        self.save()
        if is_exhausted:
            self.finalise()
        return self.price * added_units / self.used_so_far

    def __str__(self):
        return self.res_name + " (" + str(self.id) + ")"

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
    meal_cost   = models.FloatField(default=0)      #   to be deprecated
    open_cost   = models.FloatField(default=0)
    closed_cost = models.FloatField(default=0)
    dish_deps   = models.IntegerField(default=0)
    meal_owner  = models.ForeignKey(User)

    def updatePriceDelta(self, delta):
        self.meal_cost += delta
        self.save()

    def refreshCosts(self):
        dishes = Dish.objects.filter(par_meal=self)
        self.open_cost = sum([ dish.get_open_cost() for dish in dishes ])
        self.closed_cost = sum([ dish.get_closed_cost() for dish in dishes ])
        self.save()

    def add_dep(self):
        self.dish_deps += 1
        self.save()

    def close_dep(self):
        self.dish_deps -= 1
        self.save()

    def __str__(self):
        return self.meal_type + " on " + self.cons_time.strftime("%B %-d, %Y")

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
    open_cost       = models.FloatField(default=0)

    def updatePriceDelta(self, delta):
        #   Add the delta to the meal price
        self.open_cost += delta
        self.save()

        self.par_meal.updatePriceDelta(delta)

    def add_dep(self, dep_cost):
        self.ticket_deps += 1
        self.open_cost += dep_cost
        self.save()

        self.par_meal.updatePriceDelta(dep_cost)
        if self.ticket_deps == 1:
            self.par_meal.add_dep()

    def close_dep(self, dep_cost):
        self.ticket_deps -= 1
        self.open_cost -= dep_cost
        self.save()

        if self.ticket_deps <= 0:
            self.par_meal.close_dep()

    def get_closed_cost(self):
        tickets = Resource_Ticket.objects.filter(par_dish=self, finalised=True)
        return sum([ ticket.ticket_cost for ticket in tickets ])

    def get_open_cost(self):
        tickets = Resource_Ticket.objects.filter(par_dish=self, finalised=False)
        return sum([ ticket.ticket_cost for ticket in tickets ])

    def __str__(self):
        return self.cooking_style

class TicketManager(models.Manager):
    def create_ticket(self, resource_inst, used_on_ticket, dish,
        resource_exhausted=False):
        #   Reject the ticket if used is 0
        if used_on_ticket <= 0:
            return False
        ticket = self.create(
            resource_inst   = resource_inst,
            used_on_ticket  = used_on_ticket,
            ticket_cost     = resource_inst.update_usage(
                                used_on_ticket, resource_exhausted),
            finalised       = resource_exhausted,
            par_dish        = dish
        )
        ticket.save()
        ticket.par_dish.add_dep(ticket.ticket_cost)
        if ticket.finalised:
            ticket.par_dish.close_dep(ticket.ticket_cost)
        return ticket

class Resource_Ticket(models.Model):
    resource_inst   = models.ForeignKey(Resource_Inst)
    used_on_ticket  = models.FloatField()
    ticket_cost     = models.FloatField()
    finalised       = models.BooleanField(default=False)
    par_dish        = models.ForeignKey(Dish)

    objects = TicketManager()

    def updatePrice(self, newPrice):
        #   We need to find all the dishes and update the price
        delta = newPrice - self.ticket_cost
        self.ticket_cost = newPrice
        self.save()
        self.par_dish.updatePriceDelta(delta)

    def finalise(self):
        #   We need to find the meal and see if it can be finalised
        self.finalised = True
        self.save()
        self.par_dish.close_dep(self.ticket_cost)

    def __str__(self):
        return self.resource_inst.res_name
