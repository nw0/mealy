from django import forms
from django.forms import formset_factory
from django.forms.extras.widgets import SelectDateWidget
import datetime
from .models import Resource_Inst, Meal, Dish

class Html5DateInput(forms.DateInput):
    input_type = 'date'

class MealForm(forms.Form):
    meal_date   = forms.DateField(label='Meal date',
                        initial=datetime.date.today,
                        widget=Html5DateInput(format='%Y-%m-%d'))
    meal_type   = forms.ChoiceField(label="Which meal",
                        choices=[("Lunch", "Lunch"), ("Dinner", "Dinner")])

class DishForm(forms.Form):
    dish_style  = forms.ChoiceField(choices=[
                        ('frying',      "Fried"),
                        ('boiling',     "Boiled"),
                        ('baking',      "Baked"),
                        ('roasting',    "Roasted"),
                        ('instant',     "Microwaved"), ])
    dish_style.widget.attrs.update({'autofocus': 'autofocus'})

class TicketForm(forms.Form):
    resource_inst   = forms.ModelChoiceField(
                            queryset = Resource_Inst.objects.filter(
                                        exhausted = False).order_by('id'))
    resource_inst.widget.attrs.update({'autofocus': 'autofocus'})
    units_used      = forms.FloatField()
    exhausted       = forms.BooleanField()

TicketFormSet = formset_factory(TicketForm, extra=2)

class InstAttribForm(forms.Form):
    price   = forms.IntegerField()
