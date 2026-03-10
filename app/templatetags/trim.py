from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def trim(value: str) -> str:
    return value.strip()
