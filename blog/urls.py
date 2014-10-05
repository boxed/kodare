from django.conf.urls import *
from django.views.generic import DetailView, ListView
from kodare.blog.models import Entry

urlpatterns = patterns('',
    (r'^$', ListView.as_view(queryset=Entry.objects.order_by('-creation_time'), paginate_by=5, template_name='blog.html')),
    (r'^(?P<slug>.*)/$', DetailView.as_view(queryset=Entry.objects.all()))
)
