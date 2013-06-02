from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', {'packages': 'django.conf'}),

    (r'^admin/(.*)', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'f:/kodare/django/contrib/admin/media'}),
        
    # static content
    (r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('kodare.countdown.views',
    (r'^$',  'index'), 
    (r'^create/$',  'create_countdown'),
    (r'^(?P<countdown_id>\d+)/$', 'view_countdown'),
    (r'^(?P<countdown_id>\d+)/edit/$', 'edit_countdown'),
    (r'^add_notification/$',  'add_notification'),
)

urlpatterns += patterns('',
    (r'^countdown.css$', 'curia.base.views.stylesheet', {'template':'countdown.css'}),
)