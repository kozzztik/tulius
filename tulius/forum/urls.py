from django.conf import urls

from tulius.forum.threads import api as threads_api
from tulius.forum.collapse_threads import views as collapse_views
from tulius.forum import online_status
from tulius.forum.comments import api as comments_api
from tulius.forum.rights import api as rights_api
from tulius.forum.voting import views as voting
from tulius.forum.other import likes
from tulius.forum.other import readmarks

app_name = 'tulius.forum'

urlpatterns = [
    urls.url(r'^$', threads_api.IndexView.as_view(), name='index'),
    urls.url(r'^favorites/$', likes.Favorites.as_view(), name='favorites'),
    urls.url(
        r'^granted_rights/$',
        rights_api.GrantedRightsAPI.as_view(), name='index_rights'),
    urls.url(
        r'^read_mark/$',
        readmarks.ReadmarkAPI.as_view(), name='index_readmark'),
    urls.url(
        r'^collapse/$',
        collapse_views.CollapseAPIList.as_view(), name='collapse_list'),
    urls.url(
        r'^collapse/(?P<pk>\d+)$',
        collapse_views.CollapseAPISave.as_view(), name='collapse_save'),
    urls.url(
        r'^online_status/$',
        online_status.OnlineStatusAPI.as_view(), name='online_status_all'),
    urls.url(
        r'^online_status/(?P<pk>\d+)/$',
        online_status.OnlineStatusAPI.as_view(), name='online_status'),
    urls.url(
        r'^thread/(?P<pk>\d+)/$',
        threads_api.ThreadView.as_view(), name='thread'),
    urls.url(
        r'^thread/(?P<pk>\d+)/comments_page/$',
        comments_api.CommentsPageAPI.as_view(), name='comments_page'),
    urls.url(
        r'^thread/(?P<pk>\d+)/read_mark/$',
        readmarks.ReadmarkAPI.as_view(), name='thread_readmark'),
    urls.url(
        r'^thread/(?P<pk>\d+)/granted_rights/$',
        rights_api.GrantedRightsAPI.as_view(), name='thread_rights'),
    urls.url(
        r'^thread/(?P<pk>\d+)/granted_rights/(?P<right_id>\d+)/$',
        rights_api.GrantedRightAPI.as_view(), name='thread_right'),
    urls.url(
        r'^comment/(?P<pk>\d+)/$',
        comments_api.CommentAPI.as_view(), name='comment'),
    urls.url(
        r'^comment/(?P<pk>\d+)/voting/$',
        voting.VotingAPI.as_view(), name='voting'),
    urls.url(
        r'^likes/$',
        likes.Likes.as_view(), name='likes'),
]
