import os
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.contrib.localflavor.us.models import PhoneNumberField, USStateField
from django.db import models
from django.template.defaultfilters import slugify
from invoicer.utils import generate_next_invoice_number
from invoicer.utils import get_company

__all__ = ['Client', 'Company', 'Terms', 'LineItem', 'InvoiceManager',
            'Invoice', 'Item']

# class Entity(models.Model):
#     name = models.CharField(max_length=128)
#     contact_person = models.CharField(max_length=128, blank=True)
#     address = models.CharField(max_length=100, blank=True)
#     city = models.CharField(max_length=60, blank=True)
#     state = USStateField(blank=True)
#     zip_code = models.CharField(max_length=10, blank=True)
#     phone_number = PhoneNumberField(blank=True)
#     email = models.EmailField(max_length=80, blank=True)

#     class Meta:
#         abstract = True

#     def __unicode__(self):
#         return self.name

#     def full_address(self):
#         return "%s, %s, %s %s" %(self.address, self.city, self.state, self.zip_code,)

class Client(models.Model):
    name = models.CharField(max_length=128)
    vat_id = models.CharField(max_length=32, blank=True)
    fiscal_code = models.CharField(max_length=32, blank=True)
    administrative_address = models.TextField(blank=True)
    delivery_address = models.TextField(blank=True)
    #project = models.CharField(max_length=128, blank=True)

    @models.permalink
    def get_absolute_url(self):
        return ('invoicer:client', (), {'id':self.id})

    def receipts_to_date(self):
        items = LineItem.objects.filter(invoice__client=self).only("price", "quantity", "taxable", "invoice__company__tax_rate").select_related("invoice__company")
        total = 0
        for item in items:
            total += item.total()
        return total

    def __unicode__(self):
        return self.name

class Company(models.Model):
    #website = models.URLField(max_length=100, blank=True)
    #numbering_prefix = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=60, blank=True)
    billing_email = models.EmailField(max_length=80, blank=True)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)
    use_compact_invoice = models.BooleanField(default = False)

    logo = models.ImageField(max_length=512, blank=True, default='', upload_to='logo')
    invoice_footer = models.TextField(blank=True)
    #invoice_stylesheet = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    @models.permalink
    def get_absolute_url(self):
        return ('invoicer:company', (), {'id':self.id})

    def tax_multiplier(self):
        return self.tax_rate/100 + 1


class Terms(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=256)

    class Meta:
        verbose_name_plural = "Terms"

    def __unicode__(self):
        return self.name

class AbstractItem(models.Model):
    name = models.TextField(blank=True)
    description = models.CharField(max_length=256, blank=True)
    #cost = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    taxable = models.BooleanField(default = True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.name)

class LineItem(AbstractItem):
    item = models.ForeignKey("Item", blank=True, null=True)
    quantity = models.DecimalField(max_digits=7, decimal_places=2, default="1")
    invoice = models.ForeignKey("Invoice", related_name="line_items", editable=False)

    class Meta:
        verbose_name = "Line Item"
        verbose_name_plural = "Line Items"

    def ext_price(self):
        ext_price = self.price * self.quantity
        return ext_price.quantize(Decimal('.01'))

    def total(self):
        total = self.ext_price()
        if self.taxable:
            total = total * self.invoice.company.tax_multiplier()
        return total.quantize(Decimal('.01'))

    def save(self, *args, **kwargs):
        if self.item_id is not None:
            self.name = self.item.name
            self.description = self.item.description
            #self.cost = self.item.cost
            self.price = self.item.price
            self.taxable = self.item.taxable
        super(LineItem, self).save(*args, **kwargs)

class InvoiceManager(models.Manager):
    def get_query_set(self):
        return super(InvoiceManager, self).get_query_set().none()

class Invoice(models.Model):
    objects = models.Manager()
    manager = InvoiceManager()
    STATUS_CHOICES = (
        ("unsent", "Unsent"),
        ("sent", "Sent"),
        ("partial", "Partial Payment"),
        ("paid", "Paid In Full"),
        ("other", "Other"),
    )
    company = models.ForeignKey(Company, related_name='invoices')
    location = models.CharField(max_length=60, blank=True)
    client = models.ForeignKey(Client, related_name='invoices')
    left_address = models.TextField(blank=True)
    right_address = models.TextField(blank=True)
    invoice_date = models.DateField(default=date.today)
    year = models.IntegerField()
    number = models.IntegerField(blank=True, help_text='leave empty for automatic assignment')
    due_date = models.DateField(default=date.today)
    status = models.CharField(max_length=10, default="unsent", choices=STATUS_CHOICES)
    status_notes = models.CharField(max_length=128, blank=True)
    terms = models.ForeignKey(Terms, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)
    footer = models.TextField(blank=True)

    class Meta:
        ordering = ('-year', '-number',)
        unique_together = (('company', 'number', 'year',),)

    @models.permalink
    def get_absolute_url(self):
        return ('invoicer:invoice', (), {'year':self.year, 'number':self.number,})

    def __unicode__(self):
        return '%d/%d' % (self.number, self.year)

    #def get_invoice_number(self):
    #    return "%s%05d" %(self.company.numbering_prefix, self.id,)

    def taxable_amount(self):
        taxable = 0
        for line in self.line_items.all():
            if line.taxable:
                taxable += line.ext_price()
        return taxable

    def tax(self):
        tax = self.taxable_amount() * self.company.tax_rate/100
        return tax.quantize(Decimal('.01'))

    def subtotal(self):
        subtotal = 0
        for line in self.line_items.all():
            subtotal += line.ext_price()
        return subtotal

    def total(self):
        total = 0
        for line in self.line_items.all():
            total += line.total()
        return total

    def fix_internal_values(self):
        dirty = False
        if self.company is None:
            self.company = get_company()
            dirty = True
        return dirty

    def save(self, force_insert=False, force_update=False):
        self.year = self.invoice_date.year
        if self.number is None:
            self.number = generate_next_invoice_number(self)
        super(Invoice, self).save(force_insert, force_update)
        #if self.fix_internal_values():
            #self.save()

#def stylesheet_upload(instance, filename):
#    file, ext = os.path.splitext(filename)
#    file_slug = '%s%s' %(slugify(file), ext,)
#    company_id = unicode(instance.company.id)
#    #upload_dir = settings.get("INVOICER_UPLOAD_DIR", "invoicer").strip("/")
#    upload_dir = getattr(settings, "INVOICER_UPLOAD_DIR", "invoicer").strip("/")
#    return os.path.join(upload_dir, "stylesheets", company_id, file_slug)
#
#class Stylesheet(models.Model):
#    company = models.ForeignKey("Company", related_name="stylesheets")
#    name = models.CharField(max_length=128)
#    description = models.CharField(max_length=256)
#    stylesheet = models.FileField(upload_to=stylesheet_upload)
#    introduction_text = models.TextField(max_length=256, blank=True)
#    feedback_text = models.TextField(max_length=256, blank=True)
#    misc_text = models.TextField(max_length=256, blank=True)
#    thank_you_text = models.TextField(max_length=256, blank=True)

class Item(AbstractItem):
    pass
