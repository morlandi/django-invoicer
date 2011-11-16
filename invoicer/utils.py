from django.db.models.aggregates import Max


def get_company():
    from invoicer.models import Company
    companies = Company.objects.all()
    if len(companies) != 1:
        raise Exception('Please configure one single company')
    return companies[0]
     
def generate_next_invoice_number( obj ):
    """    Generate a suitable invoice number for given object;
           Strategy: find out current max value for the year, then add 1
    """
    queryset = obj.__class__.objects.filter(year=obj.year)
    max = queryset.aggregate(Max('number')).values()[0]
    if max is None:
        max = 0
    return (max + 1)

