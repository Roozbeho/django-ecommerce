from django import template

register = template.Library()


@register.filter
def to_str(value):
    return str(value)


@register.simple_tag()
def multiply(val1, val2):
    return val1 * val2