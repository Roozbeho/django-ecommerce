from django import template

register = template.Library()


@register.filter
def to_str(value):
    return str(value)
