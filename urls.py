from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from kodare.blog.feeds import *

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/www-python/kodare/django/contrib/admin/media'}),

    (r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    url(r'^stats/', include('kodare.stats.urls')),
    url(r'^blog/', include('kodare.blog.urls')),
)

urlpatterns += patterns('kodare.views',
    (r'^spotify_playlist_length/', 'spotify_playlist_length'),
    (r'^syntax_highlight/$', 'syntax_highlight', {}),
    (r'^objc_to_python/$', 'objc_to_python', {}),
    (r'^objc_to_python/source/$', 'objc_to_python_source', {}),
    
    (r'^planning-calendar/$', 'sk_forum_planning_calendar', {}),
    url(r'^feed/', BlogFeed()),
    (r'^error_test/', 'error_test'),
)