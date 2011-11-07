import json

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseNotModified
from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from invoicer.forms import InvoiceForm, LineItemForm, LineItemFormset, ReducedLineItemForm
from invoicer.models import Client, Company, Invoice, LineItem

@login_required
def view_invoice(request, id):
    invoices = Invoice.objects.select_related()
    invoice = get_object_or_404(invoices, invoice_number=id)
    #stylesheet = invoice.company.stylesheets.all()[0]
    formset = LineItemFormset(instance=invoice)
    context = {
        'invoice':invoice,
        #"stylesheet":stylesheet,
        "invoice_form":InvoiceForm(),
        "formset":formset,
        "compact": invoice.company.use_compact_invoice,
    }
    return render(request, 'invoice.html', context)

@login_required
@require_POST
@csrf_exempt
def edit_invoice(request, id):
    invoices = Invoice.objects.select_related()
    invoice = get_object_or_404(invoices, invoice_number=id)
    if request.is_ajax() and request.method == "POST":
        formset = LineItemFormset(request.POST, instance=invoice)
        #invoice processing and line processing ought to be separate views
        invoice_form = InvoiceForm(request.POST, instance=invoice)
        if invoice_form.is_valid():
            invoice_form.save()
            response = {
                "status":"success",
                "value":request.POST["value"],
                "element_id":request.POST["element_id"]
            }
            return HttpResponse(json.dumps(response, separators=(',',':')), mimetype='application/json')
        elif formset.is_valid():
            formset.save()
            response = {
                "status":"success",
                "value":request.POST["value"],
                "element_id":request.POST["element_id"]
            }
            return HttpResponse(json.dumps(response, separators=(',',':')), mimetype='application/json')
        else:
            errors = {}
            for form in formset.forms:
                for field in form:
                    if field.errors:
                        errors[field.html_name] = field.errors.as_text()
            response = {"status":"error", "errors":errors}
            return HttpResponse(json.dumps(response, separators=(',',':')), mimetype='application/json')

@login_required
@csrf_exempt
def add_line(request, id):
    formClass = LineItemForm
    invoice = get_object_or_404(Invoice, invoice_number=id)
    if invoice.company.use_compact_invoice:
        formClass = ReducedLineItemForm
    if request.method == "POST":
        line = formClass(request.POST, instance=LineItem(invoice=invoice))
        if line.is_valid():
            line.save()
        return HttpResponseRedirect(invoice.get_absolute_url())
    else:
        form = formClass()
        return HttpResponse(form.as_table())

def paginate_invoices(request, entity, page):
    import pdb; pdb.set_trace() ## PDB_DEBUG ##
    set_cookie = False
    if request.method == "GET" and hasattr(request.GET, 'per_page'):
        per_page = request.GET["per_page"]
        set_cookie = True
    elif hasattr(request.COOKIES, "per_page"):
        per_page = request.COOKIES["per_page"]
    else:
        #per_page = settings.get(INVOICES_PER_PAGE, 10)
        per_page = getattr(settings, "INVOICES_PER_PAGE", 10)
    paginator = Paginator(entity.invoices, per_page)
    try:
        page = paginator.page(page)
    except (EmptyPage, InvalidPage):
        raise Http404
    context = {'entity':entity, 'invoices':page}
    resp = render(request, 'invoice_list.html', context)
    if set_cookie:
        resp.set_cookie("per_page", per_page)
    return resp

def client_invoices(request, id, page):
    client = get_object_or_404(Client.objects.select_related(), id=id)
    return paginate_invoices(request, client, page)

def company_invoices(request, id, page, per_page = 20):
    company = get_object_or_404(Company.objects.select_related(), id=id)
    return paginate_invoices(request, company, page)

def client_overview(request, id):
    client = get_object_or_404(Client.objects.select_related(), id=id)
    context = {'entity':client}
    return render(request, 'client.html', context)

def company_overview(request, id):
    company = get_object_or_404(Company.objects.select_related(), id=id)
    context = {'entity':company}
    return render(request, 'company.html', context)
