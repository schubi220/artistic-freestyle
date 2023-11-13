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
    try:
        return Event.objects.get(id=Config.get_config_value('event_id')).slug
    except:
        return False
