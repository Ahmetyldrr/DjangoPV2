from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """String'i belirtilen karaktere göre böler"""
    return value.split(arg)

@register.filter
def trim(value):
    """String'in başındaki ve sonundaki boşlukları temizler"""
    return value.strip()
