from django.conf.urls.defaults import *
from kodare.blog.models import Entry

urlpatterns = patterns('',
    (r'^$', 'django.views.generic.list_detail.object_list', {'queryset':Entry.objects.order_by('-creation_time'), 'paginate_by':5, 'template_name':'blog.html'}),
)
