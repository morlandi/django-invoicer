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
        fields = ('left_address', 'right_address', 'terms',)

class LineItemForm(forms.ModelForm):
    class Meta:
        model = LineItem
    def __init__(self, *args, **kwargs):
        super(LineItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['cols'] = 50
        self.fields['name'].widget.attrs['rows'] = 3

class ReducedLineItemForm(LineItemForm):
    class Meta:
        model = LineItem
        exclude = ('taxable', 'description', )
    # def __init__(self, *args, **kwargs):
    #     super(ReducedLineItemForm, self).__init__(*args, **kwargs)
    #     self.fields['name'].widget.attrs['cols'] = 60
    #     self.fields['name'].widget.attrs['rows'] = 3

LineItemFormset = inlineformset_factory(
    Invoice, LineItem,
    fields=('name', 'description', 'price', 'quantity', 'taxable',),
    extra=0
)
