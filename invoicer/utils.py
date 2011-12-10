from django.db.models.aggregates import Max
from datetime import datetime


def get_company():
    from invoicer.models import Company
    companies = Company.objects.all()
    if len(companies) != 1:
        raise Exception('Please configure one single company')
    return companies[0]


def generate_next_invoice_number(obj):
    """    Generate a suitable invoice number for given object;
           Strategy: find out current max value for the year, then add 1
    """
    queryset = obj.__class__.objects.filter(year=obj.year)
    max = queryset.aggregate(Max('number')).values()[0]
    if max is None:
        max = 0
    return (max + 1)


def i18n_date_format(request):
    try:
        lang_code = getattr(request, 'LANGUAGE_CODE')
    except:
        raise Exception('Did you forget LocaleMiddleware ?')
    if lang_code == 'en' or lang_code.startswith('en_'):
        date_format = 'm/d/Y'
    else:
        date_format = 'd/m/Y'
    return date_format


def duplicate_invoice(invoice):
    """ Return the new invoice, already saved in the database
    """
    from invoicer.models import Invoice
    from invoicer.models import LineItem

    # copy main attributes
    new_invoice = Invoice(
        company=invoice.company,
        invoice_date=datetime.now(),
        client=invoice.client,
        location=invoice.location,
        tax_rate=invoice.tax_rate,
        left_address=invoice.left_address,
        right_address=invoice.right_address,
        terms=invoice.terms,
        footer=invoice.footer
    )
    new_invoice.save()

    # now line items
    for line_item in invoice.line_items.all():
        new_invoice.line_items.add(LineItem(
            name=line_item.name,
            description=line_item.description,
            price=line_item.price,
            taxable=line_item.taxable,
            item=line_item.item,
            quantity=line_item.quantity
        ))

    return new_invoice
