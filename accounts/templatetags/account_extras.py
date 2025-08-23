from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Split a string by a delimiter"""
    if value:
        return value.split(arg)
    return []

@register.filter
def strip(value):
    """Strip whitespace from string"""
    if value:
        return value.strip()
    return value
