from django import template

register = template.Library()


@register.filter
def trim(value: object) -> str:
    return str(value).strip()
