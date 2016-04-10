from django import forms
from django.forms import formset_factory
from django.forms.extras.widgets import SelectDateWidget

from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt

import datetime
from .models import Resource_Type, Resource_Inst, Meal, Dish

class Html5DateInput(forms.DateInput):
    input_type = 'date'

class DatalistWidget(forms.Select):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        output = [  format_html( '<input type="text"{} list="{}">',
                                flatatt(final_attrs), name),
                    format_html('<datalist name="{}" id="{}">', name, name), ]
        options = self.render_options(choices, [value])
        if options:
            output.append(options)
        output.append('</datalist>')
        return mark_safe('\n'.join(output))

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

class NewInstForm(forms.Form):
    res_name    = forms.CharField(  label       = "Item name",
                                    max_length  = 40, )
    res_type    = forms.ModelChoiceField( label = "Type",
                                    queryset    = Resource_Type.objects.all(),
                                    widget      = DatalistWidget,
                                to_field_name   = 'r_name', )
    price       = forms.IntegerField(   label   = "Price (pence)",
                                    min_value   = 0, )
    orig_units  = forms.CharField(      label   = "Original units",
                                    max_length  = 6, )
    qty         = forms.IntegerField(   label   = "Quantity",
                                    min_value   = 0, )
    #use_formal  = forms.BooleanField(   label   = "Use formal units",
    #                                required    = False, )
    bb_date     = forms.DateTimeField(  label   = "Best before",
                                    widget      = Html5DateInput(), )
    use_bbf     = forms.ChoiceField(    label   = "Expiry type",
                                    widget      = forms.RadioSelect,
                                    choices     = [ ('bbf', "Best Before"),
                                                    ('exp', "Expires"), ],
                                    initial     = 'bbf', )
    purchase_date   = forms.DateTimeField(label = "Purchase date",
                                    widget      = Html5DateInput(
                                                        format='%Y-%m-%d'),
                                    initial     = datetime.date.today)

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
    price   = forms.IntegerField(min_value=0)
