from django.contrib import admin

# Register your models here.
from .models import Resource_Inst, Resource_Ticket, Resource_Type, Meal, Dish
admin.site.register(Resource_Type)
admin.site.register(Resource_Inst)
admin.site.register(Resource_Ticket)
admin.site.register(Dish)

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display    = ('__str__', 'meal_owner', 'cons_time', 'meal_type')
    list_filter     = ('meal_owner', 'meal_type')

def other_checks(user):
    #   Use this function for checks which the user must pass to use Mealy
    #   If there are none, simply return True
    return user.groups.filter(name="Mealy Users")
