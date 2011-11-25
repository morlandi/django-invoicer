#import json
from django.utils import simplejson
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
from invoicer.utils import i18n_date_format
from django.utils.safestring import mark_safe
from time import sleep
from django.contrib import messages
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _
from django.template.context import RequestContext
from django.shortcuts import render_to_response


def dump_post_items(request, prompt):
    if settings.DEBUG:
        print ''
        print '---------- ' + prompt + ':'
        # for key, value in request.POST.items():
        #     print '%s: "%s"' % (key, value)
        lines = []
        for key, value in request.POST.items():
            lines.append('%s: "%s"' % (key, value))
        lines.sort()
        for line in lines:
            print line

@login_required
def view_invoice(request, year, number):

    invoices = Invoice.objects.select_related()
    invoice = get_object_or_404(invoices, year=int(year), number=int(number))
    formset = LineItemFormset(instance=invoice)
    context = {
        'invoice': invoice,
        "invoice_form": InvoiceForm(),
        "formset": formset,
        "date_format": i18n_date_format(request),
        "compact": invoice.company.use_compact_invoice,
    }
    messages.warning(request, i18n_date_format(request))
    return render_to_response('invoice.html', context, context_instance=RequestContext(request))

@login_required
@require_POST
@csrf_exempt
def edit_invoice(request, year, number):
    if not request.user.is_staff:
        raise Exception(unicode(_(u'Not authorized')))
    invoices = Invoice.objects.select_related()
    invoice = get_object_or_404(invoices, year=int(year), number=int(number))
    original_invoice_year = invoice.invoice_date.year
    errors = {}

    if request.is_ajax() and request.method == "POST":

        dump_post_items(request,'edit_invoice')

        form = InvoiceForm(request.POST, instance=invoice)
        formset = LineItemFormset(request.POST, instance=invoice)

        if form.is_valid() and formset.is_valid():
            # Check date: change of year is not allowed
            if form.cleaned_data['invoice_date'].year != original_invoice_year:
                errors[''] = unicode(_(u'Cannot modify invoice year'))
            else:
                form.save()
                formset.save()
                response = {
                    "status": "success",
                    "value": request.POST["_value"],
                    "element_id": request.POST["_element_id"]
                }
                return HttpResponse(simplejson.dumps(response, ensure_ascii=False, separators=(',',':')), mimetype='application/json')
        else:
            for field in form:
                if field.errors:
                    errors[field.html_name] = field.errors.as_text()
            for form in formset.forms:
                for field in form:
                    if field.errors:
                        errors[field.html_name] = field.errors.as_text()

    response = {"status":"error", "errors":errors}
    return HttpResponse(simplejson.dumps(response, ensure_ascii=False, separators=(',',':')), mimetype='application/json')

@login_required
@csrf_exempt
def add_line(request, year, number):

    dump_post_items(request,'add_line')

    if not request.user.is_staff:
        raise Exception(unicode(_(u'Not authorized')))
    formClass = LineItemForm
    invoice = get_object_or_404(Invoice, year=int(year), number=int(number))
    if invoice.company.use_compact_invoice:
        formClass = ReducedLineItemForm
    if request.method == "POST":
        line = formClass(request.POST, instance=LineItem(invoice=invoice))
        if line.is_valid():
            line.save()
            messages.info(request, 'New line added')
        else:
            for key in line.errors:
                messages.error(request, '%s: %s' % (key, strip_tags(line.errors[key])))
        return HttpResponseRedirect(invoice.get_absolute_url())
    else:
        form = formClass()
        return HttpResponse(form.as_table())

@login_required
@csrf_exempt
def delete_lines(request, year, number):
    try:
        if not request.user.is_staff:
            raise Exception(unicode(_(u'Not authorized')))
        invoice = get_object_or_404(Invoice, year=int(year), number=int(number))
        line_item_ids = [int(item) for item in request.POST['line_item_ids'].split(',')]
        # make sure all line items pertain to this invoice
        invoice_line_items = [item.id for item in invoice.line_items.all()]
        for line_item_id in line_item_ids:
            if not line_item_id in invoice_line_items:
                raise Exception(unicode(_(u'Invalid line item specified')))
        line_items = LineItem.objects.filter(invoice=invoice,id__in=line_item_ids)
        n = len(line_items)
        line_items.delete()
        if n==1:
            messages.info(request, _(u'1 line item deleted'))
        else:
            messages.info(request, _(u'%d line items deleted') % n)
    except Exception, e:
        messages.error(request, e.message)
    return HttpResponse('ok')

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
