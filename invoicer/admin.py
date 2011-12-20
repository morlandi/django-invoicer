from django.contrib import admin

from invoicer.models import LineItem
from invoicer.models import Item
from invoicer.models import Invoice
from invoicer.models import Company
from invoicer.models import Client
from invoicer.models import Terms
from invoicer.forms import InvoiceCreationForm
from invoicer.utils import get_active_company
from invoicer.utils import get_active_company_pk
from invoicer.admin_views import admin_import_data
from django.utils.translation import ugettext_lazy as _
from django.db import transaction
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.conf import settings
from django.utils.safestring import mark_safe
from django.http import HttpResponseRedirect
import traceback
import sys
from django.utils.encoding import force_unicode
from django.http import HttpResponse
from django.utils.html import escape
from django.utils.html import escapejs
from django.shortcuts import get_object_or_404
from invoicer.utils import duplicate_invoice


class LineItemInline(admin.TabularInline):
    model = LineItem
    fields = ("item", "name", "price", "quantity", "taxable", "position",)
    extra = 0

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs["queryset"] = Item.objects.for_user(request)
        return super(LineItemInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class InvoiceInline(admin.TabularInline):
    fields = ("__unicode__", "invoice_date", "gross_total", "locked", "paid", "due_date", )
    readonly_fields = ("__unicode__", "invoice_date", "gross_total", "locked", "paid", "due_date", )
    model = Invoice
    max_num = 0
    extra = 0

#class StylesheetInline(admin.StackedInline):
#    model = Stylesheet
#    extra = 1
#    max_num = 1


class CompanyAdmin(admin.ModelAdmin):
    # fieldsets = (
    #     (None, {
    #         "fields": ("name", "numbering_prefix", "billing_email", "tax_rate", "use_compact_invoice", ),
    #     },),
    #     ("Contact Info", {
    #         "fields": ("contact_person", "phone_number", "email", "website"),
    #     },),
    #     ("Address", {
    #         "fields": ("address", "city", "state", "zip_code",), "classes": ("wide",)
    #     },),
    #     ("Invoices customization", {
    #         "fields": ("invoice_stylesheet", "invoice_footer", "logo",), "classes": ("wide",)
    #     },),
    # )
    model = Company
    #inlines = (StylesheetInline,)
    filter_horizontal = ('authorized_users', )


class CompanySpecificBaseModelAdmin(admin.ModelAdmin):

    # filter main object list based on active system
    def queryset(self, request):
        return self.model.objects.for_user(request)

    def save_model(self, request, obj, form, change):
        # automatically assign the active system to the created/modified object
        try:
            active_company = get_active_company(request)
        except Exception, e:
            messages.error(request, e.message)
            return
        obj.company = active_company
        super(CompanySpecificBaseModelAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "company":
            kwargs["queryset"] = Company.objects.filter(pk=get_active_company_pk(request))
        elif db_field.name == "client":
            kwargs["queryset"] = Client.objects.for_user(request)
        elif db_field.name == "item":
            kwargs["queryset"] = Item.objects.for_user(request)
        elif db_field.name == "terms":
            kwargs["queryset"] = Terms.objects.for_user(request)
        return super(CompanySpecificBaseModelAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


class ClientAdmin(CompanySpecificBaseModelAdmin):
    model = Client
    list_display = ('name', 'vat_id', 'fiscal_code', 'receipts_to_date')
    search_fields = ('name', '=vat_id', '=fiscal_code', )

    inlines = (InvoiceInline,)

    fieldsets = (
        (None, {
            "fields": ('name', 'vat_id', 'fiscal_code', 'email',),
        },),
        (_(u'Addresses'), {
            'classes': ('collapse',),
            "fields": ('administrative_address', 'delivery_address', 'bank_address',),
        },),
    )

    def get_urls(self):
        urls = super(ClientAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^import-clients/$', self.admin_site.admin_view(self.do_import_clients), {}, name="invoicer-import-clients"),
        )
        return my_urls + urls

    @transaction.commit_manually
    def do_import_clients(self, request):
        next = reverse('admin:invoicer_client_changelist', args=())
        try:
            response = admin_import_data(request, self, next)
            transaction.commit()
        except Exception, e:
            transaction.rollback()
            messages.error(request, str(e))
            if settings.DEBUG:
                messages.warning(request, mark_safe("<br />".join(traceback.format_tb(sys.exc_info()[2]))))
            return HttpResponseRedirect(next)
        return response


class TermsAdmin(CompanySpecificBaseModelAdmin):
    model = Terms


class ItemAdmin(CompanySpecificBaseModelAdmin):
    model = Item


class InvoiceAdmin(CompanySpecificBaseModelAdmin):
    add_form = InvoiceCreationForm
    model = Invoice
    list_display = ("__unicode__", 'view_on_site', "number", "year", "client", "net_total", "gross_total", "locked", "paid", "invoice_date", "due_date", )
    list_filter = ("year", "invoice_date", "due_date", "locked", "paid", "client", )
    search_fields = ("number", "client__name")
    readonly_fields = ("company", "year", 'net_total', 'gross_total',)
    date_hierarchy = 'invoice_date'
    fieldsets = (
        (None, {"fields": (("number", "client", "tax_rate", "company",),
            ("invoice_date", "location", "year",),
            ("net_total", "gross_total"), ("terms", "due_date",),
            ("locked", "paid", "paid_date", "notes",), 'footer', )}),
        ('Address', {'fields': (('left_address', 'right_address',),), }),
    )
    add_fieldsets = (
        (None, {"fields": ('number', 'client', 'invoice_date', )}),
    )
    inlines = (LineItemInline,)

    def view_on_site(self, obj):
        url = obj.get_absolute_url()
        description = unicode(_(u'Edit'))
        return '<a href="%s">%s</a>' % (url, description)
    view_on_site.allow_tags = True
    view_on_site.short_description = _(u'View on site')

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super(InvoiceAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults.update({
                'form': self.add_form,
                'fields': admin.util.flatten_fieldsets(self.add_fieldsets),
            })
        defaults.update(kwargs)
        return super(InvoiceAdmin, self).get_form(request, obj, **defaults)

    def save_model(self, request, obj, form, change):
        obj.year = obj.invoice_date.year
        obj.company = get_active_company(request)
        if not change:
            # new invoice: fill attributes with suitable defaults
            if len(obj.client.delivery_address) == 0:
                obj.right_address = obj.client.administrative_address
            else:
                obj.right_address = obj.client.delivery_address
                obj.left_address = obj.client.administrative_address
            obj.location = obj.company.location
            obj.footer = obj.company.invoice_footer
            obj.tax_rate = obj.company.invoice_tax_rate
        super(InvoiceAdmin, self).save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Determines the HttpResponse for the add_view stage.
        Adapted from "django/contrib/admin/optons.py"
        """
        opts = obj._meta
        pk_value = obj._get_pk_val()

        msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.
        if "_continue" in request.POST:
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if "_popup" in request.POST:
                post_url_continue += "?_popup=1"
            return HttpResponseRedirect(post_url_continue % pk_value)

        if "_popup" in request.POST:
            return HttpResponse('<script type="text/javascript">opener.dismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                # escape() calls force_unicode.
                (escape(pk_value), escapejs(obj)))
        elif "_addanother" in request.POST:
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)
            # Redirect to in-page editing view
            post_url = obj.get_absolute_url()
            return HttpResponseRedirect(post_url)

    def get_urls(self):
        urls = super(InvoiceAdmin, self).get_urls()
        my_urls = patterns('',
            url(r'^import-invoices/$', self.admin_site.admin_view(self.do_import_invoices), {}, name="invoicer-import-invoices"),
            url(r'^(?P<object_id>[\d]+)/duplicate_invoice/$', self.admin_site.admin_view(self.do_duplicate_invoice), {}, name="invoicer-duplicate-invoice"),
        )
        return my_urls + urls

    @transaction.commit_manually
    def do_import_invoices(self, request):
        next = reverse('admin:invoicer_invoice_changelist', args=())
        try:
            response = admin_import_data(request, self, next)
            transaction.commit()
        except Exception, e:
            transaction.rollback()
            messages.error(request, str(e))
            if settings.DEBUG:
                messages.warning(request, mark_safe("<br />".join(traceback.format_tb(sys.exc_info()[2]))))
            return HttpResponseRedirect(next)
        return response

    @transaction.commit_on_success
    def do_duplicate_invoice(self, request, object_id):
        invoice = get_object_or_404(Invoice, pk=int(object_id))
        try:
            new_invoice = duplicate_invoice(invoice)
            messages.info(request, unicode(_(u'Invoice has correctly been duplicated')))
            url = new_invoice.get_absolute_url()
            transaction.commit()
        except Exception, e:
            transaction.rollback()
            messages.error(request, str(e))
            url = reverse('admin:invoicer_invoice_changelist', args=())
            if settings.DEBUG:
                messages.warning(request, mark_safe("<br />".join(traceback.format_tb(sys.exc_info()[2]))))
                #raise
        return HttpResponseRedirect(url)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Terms, TermsAdmin)
admin.site.register(Item, ItemAdmin)
