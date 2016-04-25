from django.contrib import admin

# Register your models here.
from .models import Resource_Inst, Resource_Ticket, Resource_Type, Meal, Dish, \
                    Standard_Inst, Unit
admin.site.register(Resource_Type)
admin.site.register(Resource_Ticket)
admin.site.register(Unit)

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display    = ('__str__', 'meal_owner', 'cons_time', 'meal_type')
    list_filter     = ('meal_owner', 'meal_type')

@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_filter     = ('par_meal__meal_owner', 'cooking_style')

@admin.register(Resource_Inst)
class InstAdmin(admin.ModelAdmin):
    list_filter     = ('inst_owner', 'exhausted', 'orig_unit', 'res_type')

@admin.register(Standard_Inst)
class StandardInstAdmin(admin.ModelAdmin):
    list_filter     = ('inst_type', 'orig_unit')

def other_checks(user):
    #   Use this function for checks which the user must pass to use Mealy
    #   If there are none, simply return True
    return user.groups.filter(name="Mealy Users")
