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

class MealForm(forms.ModelForm):
    cons_time       = forms.DateTimeField(
                            label   = 'Meal date',
                            initial = datetime.date.today,
                            widget  = Html5DateInput(format='%Y-%m-%d'), )
    meal_type       = forms.ChoiceField(
                            label   = "Which meal",
                            choices = Meal.MEAL_TYPES,
                            initial = "Lunch", )
    cons_time.widget.attrs.update({'autofocus': 'autofocus'})
    class Meta:
        model       = Meal
        fields      = [ 'cons_time', 'meal_type' ]

class DishForm(forms.ModelForm):
    cooking_style   = forms.ChoiceField(
                            label   = "Dish style",
                            choices = Dish.COOKING_STYLES,
                            initial = 'frying', )
    cooking_style.widget.attrs.update({'autofocus': 'autofocus'})
    class Meta:
        model       = Dish
        fields      = [ 'cooking_style' ]

class NewInstForm(forms.ModelForm):
    res_name        = forms.CharField(
                            label           = "Item name",
                            max_length      = 40, )
    res_type        = forms.ModelChoiceField(
                            label           = "Type",
                            queryset        = Resource_Type.objects.all(),
                            widget          = DatalistWidget,
                            to_field_name   = 'r_name', )
    price           = forms.IntegerField(
                            label           = "Price (pence)",
                            min_value       = 0, )
    units_original  = forms.CharField(
                            label           = "Original units (g, ml)",
                            max_length      = 6, )
    amt_original    = forms.IntegerField(
                            label           = "Quantity",
                            min_value       = 0, )
    best_bef_date   = forms.DateTimeField(
                            label           = "Best before",
                            widget          = Html5DateInput(), )
    best_before     = forms.BooleanField(
                            label           = "Expiry type",
                            widget          = forms.RadioSelect(choices=
                                                [   (True, 'Best Before'),
                                                    (False, 'Expiry') ] ),
                            initial         = True, )
    purchase_date   = forms.DateTimeField(
                            label           = "Purchase date",
                            widget          = Html5DateInput(format='%Y-%m-%d'),
                            initial         = datetime.date.today, )
    res_name.widget.attrs.update({'autofocus': 'autofocus'})
    class Meta:
        model       = Resource_Inst
        exclude     = [ 'inst_owner',
                        'last_mod',
                        'unit_use_formal',
                        'used_so_far',
                        'exhausted' ]

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
