#!/usr/bin/env python2
# -*- coding: latin-1 -*-
from numbers import Number
from django import template
from django.utils.html import format_html

register = template.Library()

@register.filter
def price(pr, p2 = False):
    if not isinstance(pr, Number):
        raise TypeError("Price must be a number")

    if p2 is False:
        if pr < 0.5:
            return "nothing"
        pr = round(pr, 0)
        if pr < 100:
            return "%dp" % pr
        return "£%.2f" % (pr/100)

    if not isinstance(p2, Number):
        raise TypeError("Price must be a number")

    if pr < 0.5 and p2 < 0.5:
        return "nothing"
    pr, p2 = round(pr, 0), round(p2, 0)
    if pr < 100 and p2 < 100:
        return "%dp + %dp" % (pr, p2)
    return "£%.2f + £%.2f" % (pr/100, p2/100)

@register.filter
def dish_pretty(dish):
    #   Assume that first word is the cooking style
    dish = dish.__str__().partition(" ")
    return format_html("{} <em>{}</em>", dish[0], dish[2])
