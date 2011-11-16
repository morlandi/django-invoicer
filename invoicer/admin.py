from django.contrib import admin

from invoicer.models import *
from invoicer.forms import InvoiceCreationForm
from invoicer.utils import generate_next_invoice_number
from invoicer.utils import get_company

class LineItemInline(admin.TabularInline):
    model = LineItem
    fields = ("item", "name", "cost", "price", "quantity", "taxable")
    extra = 1

class InvoiceInline(admin.TabularInline):
    fields = ("invoice_date", "status", "due_date", "company", )
    readonly_fields = ("invoice_date", "due_date", "company",)
    model = Invoice
    max_num = 0
    extra = 0

class StylesheetInline(admin.StackedInline):
    model = Stylesheet
    extra = 1
    max_num = 1

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
    inlines = (StylesheetInline,)

class ClientAdmin(admin.ModelAdmin):
    model = Client
    list_display = ("name", "vat_id", "receipts_to_date")
    inlines = (InvoiceInline,)

class TermsAdmin(admin.ModelAdmin):
    model = Terms

class InvoiceAdmin(admin.ModelAdmin):
    add_form_template = 'admin/invoicer/invoice/add_form.html'
    add_form = InvoiceCreationForm
    model = Invoice
    list_display = ("__unicode__", "number", "year", "client", "company", "invoice_date", "due_date", "status",)
    list_filter = ("year", "client", "invoice_date", "due_date", "status",)
    list_editable = ("status",)
    search_fields = ("number", )
    readonly_fields = ("company", "year", )
    date_hierarchy = 'invoice_date'
    fieldsets = (
        (None, {"fields": (("number", "client", "tax_rate", "company",), ("invoice_date", "year",), ("terms", "due_date",), ("status", "status_notes",), )}),
        ('Address', {'fields': (('left_address','right_address',),),}),
    )
    add_fieldsets = (
        (None, {"fields": ('number', 'client', 'invoice_date', )}),
    )
    inlines = (LineItemInline,)
    
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
        obj.company = get_company()
        obj.year = obj.invoice_date.year
        if obj.number is None:
            obj.number = generate_next_invoice_number(obj)
        super(InvoiceAdmin, self).save_model(request, obj, form, change)

admin.site.register(Company, CompanyAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Terms, TermsAdmin)
admin.site.register(Item)
