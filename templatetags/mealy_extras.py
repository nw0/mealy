#!/usr/bin/env python2
# -*- coding: latin-1 -*-
from django import template

register = template.Library()

@register.filter
def price(pr, p2 = False):
    if p2 is False:
        if pr < 0.5:
            return "nothing"
        pr = round(pr, 0)
        if pr < 100:
            return "%dp" % pr
        return "£%.2f" % (pr/100)
    if pr < 0.5 and p2 < 0.5:
        return "nothing"
    pr, p2 = round(pr, 0), round(p2, 0)
    if pr < 100 and p2 < 100:
        return "%dp + %dp" % (pr, p2)
    return "£%.2f + £%.2f" % (pr/100, p2/100)
