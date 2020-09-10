from django.conf import urls

from tulius.forum.threads import views as threads_api
from tulius.forum.threads import counters
from tulius.forum.collapse_threads import views as collapse_views
from tulius.forum import online_status
from tulius.forum.comments import views as comments_api
from tulius.forum.rights import views as rights_api
from tulius.forum.other import likes
from tulius.forum.other import voting
from tulius.forum.other import readmarks
from tulius.forum.other import search
from tulius.forum.other import images
from tulius.forum.other import html

app_name = 'tulius.forum'

urlpatterns = [
    urls.re_path(r'^$', threads_api.IndexView.as_view(), name='index'),
    urls.re_path(
        r'^fix/$', counters.CountersFix.as_view(), name='fix_counters'),
    urls.re_path(r'^favorites/$', likes.Favorites.as_view(), name='favorites'),
    urls.re_path(r'^images/$', images.Images.as_view(), name='images'),
    urls.re_path(
        r'^uploaded_files/$',
        html.UploadFiles.as_view(), name='uploaded_files'),
    urls.re_path(
        r'^granted_rights/$',
        rights_api.GrantedRightsAPI.as_view(), name='index_rights'),
    urls.re_path(
        r'^read_mark/$',
        readmarks.ReadmarkAPI.as_view(), name='index_readmark'),
    urls.re_path(
        r'^collapse/$',
        collapse_views.CollapseAPIList.as_view(), name='collapse_list'),
    urls.re_path(
        r'^collapse/(?P<pk>\d+)$',
        collapse_views.CollapseAPISave.as_view(), name='collapse_save'),
    urls.re_path(
        r'^online_status/$',
        online_status.OnlineStatusAPI.as_view(), name='online_status_all'),
    urls.re_path(
        r'^online_status/(?P<pk>\d+)/$',
        online_status.OnlineStatusAPI.as_view(), name='online_status'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/$',
        threads_api.ThreadView.as_view(), name='thread'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/fix/$',
        counters.CountersFix.as_view(), name='fix_thread_counters'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/comments_page/$',
        comments_api.CommentsPageAPI.as_view(), name='comments_page'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/read_mark/$',
        readmarks.ReadmarkAPI.as_view(), name='thread_readmark'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/granted_rights/$',
        rights_api.GrantedRightsAPI.as_view(), name='thread_rights'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/granted_rights/(?P<right_id>\d+)/$',
        rights_api.GrantedRightAPI.as_view(), name='thread_right'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/search/$',
        search.Search.as_view(), name='thread_search'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/move/$',
        threads_api.MoveThreadView.as_view(), name='thread_move'),
    urls.re_path(
        r'^thread/(?P<pk>\d+)/restore/$',
        threads_api.RestoreThreadView.as_view(), name='restore_thread'),
    urls.re_path(
        r'^comment/(?P<pk>\d+)/$',
        comments_api.CommentAPI.as_view(), name='comment'),
    urls.re_path(
        r'^comment/(?P<pk>\d+)/voting/$',
        voting.VotingAPI.as_view(), name='voting'),
    urls.re_path(
        r'^likes/$',
        likes.Likes.as_view(), name='likes'),
]
