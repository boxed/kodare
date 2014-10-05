from django.conf.urls import *

urlpatterns = patterns('kodare.stats.views',
    (r'^$', 'index'),
    (r'^graph/(?P<category_name>.*)/$', 'graph'),
)
