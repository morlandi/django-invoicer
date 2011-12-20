from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from invoicer.models import *
from invoicer.xls_tools import XlsImporter


class InvoiceCreationForm(forms.ModelForm):

    class Meta:
        model = Invoice
        fields = ('number', 'client', 'invoice_date',)


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ('invoice_date', 'left_address', 'right_address', 'due_date', 'terms', 'tax_rate')


class LineItemForm(forms.ModelForm):

    class Meta:
        model = LineItem

    def __init__(self, invoice, *args, **kwargs):
        super(LineItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['cols'] = 50
        self.fields['name'].widget.attrs['rows'] = 3
        self.fields['item'].queryset = Item.objects.filter(company=invoice.company)


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
    fields=('name', 'description', 'price', 'quantity', 'taxable', ),
    extra=0
)


class ImportDataForm(forms.Form):
    attachment = forms.FileField()

    def save(self, request, klass):
        attachment = self.cleaned_data['attachment']
        xls_importer = XlsImporter(request, attachment, klass)
        count = xls_importer.import_all_rows()
        return count
