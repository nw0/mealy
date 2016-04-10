from django import forms
from django.forms import formset_factory
from django.forms.extras.widgets import SelectDateWidget
import datetime
from .models import Resource_Inst, Meal, Dish

class Html5DateInput(forms.DateInput):
    input_type = 'date'

class MealForm(forms.Form):
    meal_date   = forms.DateTimeField(label='Meal date',
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
                            queryset = Resource_Inst.objects.all())
    resource_inst.widget.attrs.update({'autofocus': 'autofocus'})
    units_used      = forms.FloatField(min_value=0)
    exhausted       = forms.BooleanField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['resource_inst'].queryset \
            = Resource_Inst.objects.filter(exhausted = False, inst_owner=user) \
                                    .order_by('id')

TicketFormSet = formset_factory(TicketForm, extra=2)

class InstAttribForm(forms.Form):
    price   = forms.IntegerField()
