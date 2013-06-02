from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': 'django.conf'}),

    (r'^admin/(.*)', admin.site.root),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/www-python/kodare/django/contrib/admin/media'}),
        
    # static content
    (r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('kodare.iphone_sync.views',
    (r'^$',  'index'), 
    (r'^sync/$',  'sync'), 
    url(r'^favicon.ico', 'favicon'),
)