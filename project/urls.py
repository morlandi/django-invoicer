
from django.conf.urls.defaults import patterns
from django.conf.urls.defaults import include
from django.conf import settings
from django.views.generic.simple import redirect_to

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': '/admin/'}),
    (r'^admin/', include(admin.site.urls)),
    (r'', include('invoicer.urls', namespace='invoicer', app_name='invoicer')),
)

if settings.DEVELOPMENT or settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': settings.MEDIA_ROOT}),
    )
