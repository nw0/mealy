from django import forms
from django.forms import formset_factory
from django.forms.extras.widgets import SelectDateWidget

from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.forms.utils import flatatt

import datetime
from .models import Resource_Type, Resource_Inst, Meal, Dish, Standard_Inst, \
                    Unit

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
    orig_unit       = forms.ModelChoiceField(
                            label           = "Units",
                            queryset        = Unit.objects.all(), )
    amt_original    = forms.FloatField(
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

    class Meta:
        model       = Resource_Inst
        exclude     = [ 'inst_owner',
                        'last_mod',
                        'unit_use_formal',
                        'used_so_far',
                        'exhausted' ]

class NewInstStdForm(forms.ModelForm):
    std_inst        = forms.ModelChoiceField(
                            label           = "Standard instance",
                            queryset        = Standard_Inst.objects.all(),
                            )
    price           = forms.IntegerField(
                            label           = "Price (pence)",
                            min_value       = 0, )
    amt_dummy       = forms.FloatField(
                            label           = "Amount",
                            required        = False, )
    best_bef_date   = forms.DateTimeField(
                            label           = "Best before",
                            widget          = Html5DateInput(), )
    purchase_date   = forms.DateTimeField(
                            label           = "Purchase date",
                            widget          = Html5DateInput(format='%Y-%m-%d'),
                            initial         = datetime.date.today, )
    std_inst.widget.attrs.update({'autofocus': 'autofocus'})

    class Meta:
        model       = Resource_Inst
        fields      = [ 'std_inst',
                        'price',
                        'amt_dummy',
                        'best_bef_date',
                        'purchase_date' ]

class NewStdInstForm(forms.ModelForm):
    #   New standard instances
    inst_name       = forms.CharField(
                            label           = "Instance name",
                            max_length      = 40, )
    inst_type       = forms.ModelChoiceField(
                            label           = "Type",
                            queryset        = Resource_Type.objects.all(),
                            widget          = DatalistWidget,
                            to_field_name   = 'r_name', )
    usual_price     = forms.IntegerField(
                            label           = "Usual price (pence)",
                            min_value       = 0, )
    use_formal      = forms.BooleanField(
                            label           = "Use formal units",
                            required        = False, )
    use_bestbef     = forms.BooleanField(
                            label           = "Expiry type",
                            widget          = forms.RadioSelect(choices=
                                                [   (True, 'Best Before'),
                                                    (False, 'Expiry') ] ),
                            initial         = True, )
    orig_unit       = forms.ModelChoiceField(
                            label           = "Units",
                            queryset        = Unit.objects.all(), )
    orig_amt        = forms.FloatField(
                            label           = "Quantity",
                            min_value       = 0, )

    class Meta:
        model       = Standard_Inst
        fields      = [ 'inst_name',
                        'inst_type',
                        'usual_price',
                        'use_formal',
                        'use_bestbef',
                        'is_relative',
                        'orig_unit',
                        'orig_amt' ]

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
