from django.contrib.admin.views.decorators import staff_member_required
from invoicer.forms import ImportDataForm
from django.utils.translation import ugettext_lazy as _
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib import messages
from django.http import HttpResponseRedirect

@staff_member_required
def admin_import_data(request, model_admin, next):

    klass = model_admin.model
    title = '%s %s' % (unicode(_(u'Import')), klass._meta.verbose_name_plural)

    # see http://www.slideshare.net/lincolnloop/customizing-the-django-admin
    opts = model_admin.model._meta
    admin_site = model_admin.admin_site
    has_perm = request.user.has_perm(opts.app_label+'.'+opts.get_change_permission())

    if request.method == 'POST':
        form = ImportDataForm(request.POST,request.FILES)
        if form.is_valid():
            count = form.save(request, klass)
            text = _(u'%d rows successfully imported') % count
            messages.info(request, text)
            return HttpResponseRedirect(next)
    else:
        form = ImportDataForm()

    context = {
        'admin_site': admin_site.name,
        'title': title,
        'opts': opts,
        'root_path': '/%s' % admin_site.root_path,
        'app_label': opts.app_label,
        'has_chage_permission': has_perm,
        'form': form,
    }

    return render_to_response('/admin/invoicer/import_data.html',context,
        context_instance=RequestContext(request))
