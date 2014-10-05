from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.views.generic import DetailView, YearArchiveView, MonthArchiveView, DayArchiveView
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
    (r'^SL/$', 'SL', {}),
    (r'^syntax_highlight/$', 'syntax_highlight', {}),
    (r'^objc_to_python/$', 'objc_to_python', {}),
    (r'^objc_to_python/source/$', 'objc_to_python_source', {}),
    
    (r'^very_simple/fixed_header_ajax/$', 'very_simple_fixed_header_ajax', {}),
    (r'^very_simple/fixed_header/$', 'very_simple_fixed_header', {}),
    
    (r'^planning-calendar/$', 'sk_forum_planning_calendar', {}), 
    url(r'^feed/', BlogFeed()),
    (r'^error_test/', 'error_test'),
)

 
info_dict = {
    'model': Entry,
    'date_field': 'creation_time',
}
urlpatterns += patterns('',
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', DetailView.as_view(model=Entry)),
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/(?P<day>\w{1,2})/$',               DayArchiveView.as_view(**info_dict),   info_dict),
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/$',                                MonthArchiveView.as_view(**info_dict), info_dict),
   (r'^(?P<year>\d{4})/$',                                                    YearArchiveView.as_view(**info_dict),  info_dict),
)