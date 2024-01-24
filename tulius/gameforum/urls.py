from django import urls

from tulius.gameforum import views
from tulius.gameforum.threads import views as threads
from tulius.gameforum import online_status
from tulius.gameforum.comments import views as comments
from tulius.gameforum.rights import views as rights_api
from tulius.gameforum.other import trust_marks
from tulius.gameforum.other import read_marks
from tulius.gameforum.other import views as other


app_name = 'tulius.gameforum'

urlpatterns = [
    urls.re_path(
        r'^favorites/$',
        other.Favorites.as_view(), name='favorites'),
    urls.re_path(
        r'^thread_redirrect/(?P<pk>\d+)/$',
        views.RedirrectAPI.as_view(), name='thread_redirect'),
    urls.re_path(
        r'^game/(?P<pk>\d+)/$',
        views.GameAPI.as_view(), name='game'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/$',
        views.VariationAPI.as_view(), name='variation'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/likes/$',
        other.Likes.as_view(), name='likes'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/trust_mark/(?P<role_id>\d+)/$',
        trust_marks.TrustMarkAPI.as_view(), name='trust_mark'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/$',
        threads.ThreadAPI.as_view(), name='thread'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/fix/$',
        threads.CountersFix.as_view(), name='fix_thread_counters'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/comments_page/$',
        comments.CommentsPageAPI.as_view(), name='comments_page'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/comments_sse/$',
        comments.CommentsSubscription.as_view(), name='comments_sse'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/read_mark/$',
        read_marks.ReadmarkAPI.as_view(), name='thread_readmark'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)'
        r'/granted_rights/$',
        rights_api.GrantedRightsAPI.as_view(), name='thread_rights'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/granted_rights/'
        r'(?P<right_id>\d+)/$',
        rights_api.GrantedRightAPI.as_view(), name='thread_right'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/online_status/$',
        online_status.OnlineStatusAPI.as_view(), name='online_status'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/search/$',
        other.Search.as_view(), name='thread_search'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/move/$',
        threads.MoveThreadView.as_view(), name='thread_move'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/restore/$',
        threads.RestoreThreadView.as_view(), name='restore_thread'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/comment/(?P<pk>\d+)/$',
        comments.CommentAPI.as_view(), name='comment'),
    urls.re_path(
        r'^variation/(?P<variation_id>\d+)/comment/(?P<pk>\d+)/voting/$',
        other.VotingAPI.as_view(), name='voting'),
    urls.re_path(
        r'^elastic/reindex/forum_all/$',
        other.ReindexForum.as_view(), name='elastic_reindex_forum'),
    urls.re_path(
        r'^elastic/reindex/thread/(?P<pk>\d+)/$',
        other.ReindexForum.as_view(), name='elastic_reindex_thread'),

]
