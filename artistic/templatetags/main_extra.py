from django import template
from artistic.models import Event, Config

register = template.Library()

@register.filter
def return_item(l, i):
    return l[i]

@register.filter
def percent(value: float, precision: int=0):
    return f"{value * 100.0:.{precision}f}%"

@register.simple_tag
def eventSlug():
    return Event.objects.get(id=Config.objects.get(key='event_id').value).slug
