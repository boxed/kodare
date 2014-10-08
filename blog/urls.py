from django.conf.urls import *
from django.views.generic import DetailView, ListView, DayArchiveView, MonthArchiveView, YearArchiveView
from kodare.blog.models import Entry

info_dict = {
    'model': Entry,
    'date_field': 'creation_time',
}

urlpatterns = patterns('',
    (r'^$', ListView.as_view(queryset=Entry.objects.order_by('-creation_time'), paginate_by=5, template_name='blog.html')),
    (r'^(?P<slug>.*)/$', DetailView.as_view(queryset=Entry.objects.all())),
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/(?P<day>\w{1,2})/(?P<slug>[-\w]+)/$', DetailView.as_view(model=Entry)),
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/(?P<day>\w{1,2})/$',               DayArchiveView.as_view(**info_dict),   info_dict),
   (r'^(?P<year>\d{4})/(?P<month>[a-z,A-Z]{3})/$',                                MonthArchiveView.as_view(**info_dict), info_dict),
   (r'^(?P<year>\d{4})/$',                                                    YearArchiveView.as_view(**info_dict),  info_dict),
)