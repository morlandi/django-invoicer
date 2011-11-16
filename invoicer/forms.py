from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from invoicer.models import *

class InvoiceCreationForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ('number', 'client', 'invoice_date',)
     
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('left_address', 'right_address',)

class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem

class ReducedLineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
        exclude = ('taxable', 'description', 'item', )

LineItemFormset = inlineformset_factory(
    Invoice, LineItem,
    fields=('name', 'description', 'price', 'quantity', 'taxable',),
    extra=0
)
