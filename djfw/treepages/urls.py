from django.conf.urls import *
from .views import *

urlpatterns = patterns('',
    url(r'^(?P<url>.*)$', treepage, name='treepage'),
    url(r'^pages/$', list, name='treepages_list'),
    url(r'^rebuild_treepages/$', rebuild_treepages, name='treepages_rebuild'),

)
