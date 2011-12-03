from datetime import date
from decimal import Decimal

#from django.conf import settings
#from django.contrib.localflavor.us.models import PhoneNumberField, USStateField
from django.db import models
#from django.template.defaultfilters import slugify
from django.db.models import signals
from invoicer.utils import generate_next_invoice_number
#from invoicer.utils import get_company
from invoicer.handlers import organize_files_by_pk
from django.utils.translation import ugettext_lazy as _
from positions.fields import PositionField

__all__ = ['Client', 'Company', 'Terms', 'LineItem', 'InvoiceManager',
            'Invoice', 'Item']


class Client(models.Model):
    name = models.CharField(max_length=128, unique=True)
    vat_id = models.CharField(max_length=32)
    fiscal_code = models.CharField(max_length=32, blank=True)
    email = models.EmailField(max_length=80, blank=True)
    administrative_address = models.TextField(blank=True)
    delivery_address = models.TextField(blank=True)
    bank_address = models.TextField(blank=True)

    class Meta:
        verbose_name = _(u'Client')
        verbose_name_plural = _(u'Clients')
        ordering = ['name', ]

    @models.permalink
    def get_absolute_url(self):
        return ('invoicer:client', (), {'id': self.id})

    def receipts_to_date(self):
        items = LineItem.objects.filter(invoice__client=self).only("price", "quantity", "taxable", "invoice__tax_rate").select_related("invoice__company")
        total = 0
        for item in items:
            total += item.total()
        return total

    def __unicode__(self):
        return self.name


class Company(models.Model):
    name = models.CharField(max_length=128)
    location = models.CharField(max_length=60, blank=True)
    email = models.EmailField(max_length=80, blank=True)
    invoice_tax_rate = models.DecimalField(max_digits=4, decimal_places=2)
    use_compact_invoice = models.BooleanField(default=False)
    logo = models.ImageField(max_length=512, blank=True, default='', upload_to='logo')
    invoice_footer = models.TextField(blank=True)
    bank_address = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Companies"

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('invoicer:company', (), {'id': self.id})

signals.post_save.connect(organize_files_by_pk, sender=Company)


class Terms(models.Model):
    name = models.CharField(max_length=128)
    description = models.TextField(max_length=512)

    class Meta:
        verbose_name_plural = "Terms"

    def __unicode__(self):
        return self.name


class AbstractItem(models.Model):
    name = models.TextField(blank=True)
    description = models.CharField(max_length=256, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    taxable = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        return unicode(self.name)


class LineItem(AbstractItem):
    invoice = models.ForeignKey("Invoice", related_name="line_items", editable=False)
    item = models.ForeignKey("Item", blank=True, null=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default="1")
    position = PositionField(collection=('invoice', ), verbose_name=_(u'Position'))

    class Meta:
        verbose_name = "Line Item"
        verbose_name_plural = "Line Items"
        ordering = ('position', )

    def subtotal(self):
        value = self.price * self.quantity
        return value.quantize(Decimal('.01'))

    def total(self):
        value = self.subtotal()
        if self.taxable:
            tax = value * self.invoice.tax_rate / Decimal('100.0')
            value += tax
        return value.quantize(Decimal('.01'))

    # def ext_price(self):
    #     ext_price = self.price * self.quantity
    #     return ext_price.quantize(Decimal('.01'))

    # def total(self):
    #     total = self.ext_price()
    #     if self.taxable:
    #         total = total * self.invoice.tax_rate / Decimal('100.0')
    #     return total.quantize(Decimal('.01'))

    def save(self, *args, **kwargs):
        if self.item_id is not None:
            self.name = self.item.name
            self.description = self.item.description
            self.price = self.item.price
            self.taxable = self.item.taxable
        super(LineItem, self).save(*args, **kwargs)
        self.invoice._update_cached_values()


class InvoiceManager(models.Manager):
    def get_query_set(self):
        return super(InvoiceManager, self).get_query_set().none()


class Invoice(models.Model):
    objects = models.Manager()
    manager = InvoiceManager()

    number = models.IntegerField(blank=True, help_text='leave empty for automatic assignment')
    year = models.IntegerField()
    company = models.ForeignKey(Company, related_name='invoices')
    invoice_date = models.DateField(default=date.today)
    client = models.ForeignKey(Client, related_name='invoices')
    location = models.CharField(max_length=60, blank=True)
    tax_rate = models.DecimalField(max_digits=4, decimal_places=2)
    left_address = models.TextField(blank=True)
    right_address = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    terms = models.TextField(max_length=512, blank=True)

    footer = models.TextField(blank=True)
    locked = models.BooleanField(default=False, verbose_name=_(u'Locked'), )
    paid = models.BooleanField(default=False, verbose_name=_(u'Paid'), )
    paid_date = models.DateField(null=True, blank=True)
    notes = models.TextField(max_length=512, blank=True)
    net_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    gross_total = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    class Meta:
        ordering = ('-year', '-number',)
        unique_together = (('company', 'number', 'year',),)

    @models.permalink
    def get_absolute_url(self):
        return ('invoicer:invoice', (), {'year': self.year, 'number': self.number, })

    def __unicode__(self):
        return '%d/%d' % (self.number, self.year)

    #def get_invoice_number(self):
    #    return "%s%05d" %(self.company.numbering_prefix, self.id,)

    # def taxable_amount(self):
    #     taxable = 0
    #     for line in self.line_items.all():
    #         if line.taxable:
    #             taxable += line.ext_price()
    #     return taxable

    # def tax(self):
    #     tax = self.taxable_amount() * self.tax_rate / 100.0
    #     return tax.quantize(Decimal('.01'))

    # def subtotal(self):
    #     subtotal = 0
    #     for line in self.line_items.all():
    #         subtotal += line.ext_price()
    #     return subtotal

    # def total(self):
    #     total = 0
    #     for line in self.line_items.all():
    #         total += line.total()
    #     return total

    def tax(self):
        return self.total() - self.subtotal()

    def subtotal(self):
        subtotal = 0
        for line in self.line_items.all():
            subtotal += line.subtotal()
        return subtotal

    def total(self):
        total = 0
        for line in self.line_items.all():
            total += line.total()
        return total

    def save(self, force_insert=False, force_update=False):
        self.year = self.invoice_date.year
        if self.number is None:
            self.number = generate_next_invoice_number(self)
        super(Invoice, self).save(force_insert, force_update)
        self._update_cached_values()

    def _update_cached_values(self):
        dirty = False

        new_net_total = self.subtotal()
        if self.net_total != new_net_total:
            self.net_total = new_net_total
            dirty = True

        new_gross_total = self.total()
        if self.gross_total != new_gross_total:
            self.gross_total = new_gross_total
            dirty = True

        if dirty:
            super(Invoice, self).save_base()
        return dirty


class Item(AbstractItem):
    pass
