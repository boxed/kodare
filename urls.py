from django.conf.urls.defaults import *
from kodare.blog.models import Entry
from django.conf import settings
from django.contrib import admin
from kodare.blog.feeds import *

admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^kodare/', include('kodare.foo.urls')),
    
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/www-python/kodare/django/contrib/admin/media'}),

    (r'^site-media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),

    url(r'^stats/', include('kodare.stats.urls')),
)

urlpatterns += patterns('kodare.views',
    (r'^spotify_playlist_length/', 'spotify_playlist_length'),
    (r'^SL/$', 'SL', {}),
    (r'^syntax_highlight/$', 'syntax_highlight', {}),
    (r'^objc_to_python/$', 'objc_to_python', {}),
    (r'^objc_to_python/source/$', 'objc_to_python_source', {}),
    
    (r'^very_simple/fixed_header_ajax/$',   'very_simple_fixed_header_ajax', {}),
    (r'^very_simple/fixed_header/$',        'very_simple_fixed_header', {}),
    
    (r'^planning-calendar/$', 'sk_forum_planning_calendar', {}), 
    url(r'^feed/', BlogFeed()),
)

 
info_dict = {
    'queryset': Entry.objects.all(),
    'date_field': 'creation_time',
}
urlpatterns += patterns('django.views.generic.date_based',
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', 'object_detail', info_dict),
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/(?P<day>\w{1,2})/$',               'archive_day',   info_dict),
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/$',                                'archive_month', info_dict),
   (r'^(?P<year>\d{4})/$',                                                    'archive_year',  info_dict),
)