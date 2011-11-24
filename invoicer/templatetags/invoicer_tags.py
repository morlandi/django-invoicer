from django.template.base import Library
from django.template.defaultfilters import stringfilter
from django.template.defaultfilters import floatformat
from django.utils.encoding import force_unicode
import re

register = Library()

# from "humamize" app
def _my_intcomma(value):
    """
    Converts an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    orig = force_unicode(value)
    new = re.sub("^(-?\d+)(\d{3})", '\g<1>,\g<2>', orig)
    if orig == new:
        return new
    else:
        return _my_intcomma(new)

@register.filter
def floatformatex(text, arg=-1):
    text = floatformat(text,arg).replace(',','.')
    tokens = text.split('.')
    text = _my_intcomma(tokens[0])
    if len(tokens)>1:
        text = '.'.join([text, tokens[1],])
    return text
floatformatex.is_safe = True
floatformatex = stringfilter(floatformatex)
