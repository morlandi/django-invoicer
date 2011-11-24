from django.template.base import Library
from django.template.defaultfilters import stringfilter

register = Library()

@register.filter
def normalize_floatnumber(value):
    """Converts a string into all lowercase."""
    return value.replace(',','.')
normalize_floatnumber.is_safe = True
normalize_floatnumber = stringfilter(normalize_floatnumber)

