from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from invoicer.models import *

class InvoiceForm(ModelForm):
    class Meta:
        model = Invoice

class LineItemForm(ModelForm):
    class Meta:
        model = LineItem

class ReducedLineItemForm(ModelForm):
    class Meta:
        model = LineItem
        exclude = ('taxable', 'description', 'item', 'cost' )

LineItemFormset = inlineformset_factory(
    Invoice, LineItem,
    fields=('name', 'description', 'price', 'quantity', 'taxable',),
    extra=0
)
