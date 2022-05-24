from django import template
from django.conf import settings

register = template.Library()

@register.filter
def return_item(l, i):
    return l[i]

@register.filter
def percent(value: float, precision: int=0):
    return f"{value * 100.0:.{precision}f}%"
