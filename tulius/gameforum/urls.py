from django.conf import urls

from tulius.gameforum import views
from tulius.gameforum.threads import api as threads
from tulius.gameforum import other
from tulius.gameforum import online_status
from tulius.gameforum.comments import api as comments
from tulius.gameforum.rights import api as rights_api
from tulius.gameforum.other import trust_marks


app_name = 'tulius.gameforum'

urlpatterns = [
    urls.url(
        r'^thread_redirrect/(?P<pk>\d+)/$',
        views.RedirrectAPI.as_view(), name='thread_redirect'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/$',
        views.VariationAPI.as_view(), name='variation'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/trust_mark/(?P<role_id>\d+)/$',
        trust_marks.TrustMarkAPI.as_view(), name='trust_mark'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/$',
        threads.ThreadAPI.as_view(), name='thread'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/comments_page/$',
        comments.CommentsPageAPI.as_view(), name='comments_page'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/read_mark/$',
        other.ReadmarkAPI.as_view(), name='thread_readmark'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/granted_rights/$',
        rights_api.GrantedRightsAPI.as_view(), name='thread_rights'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/granted_rights/'
        r'(?P<right_id>\d+)/$',
        rights_api.GrantedRightAPI.as_view(), name='thread_right'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/thread/(?P<pk>\d+)/online_status/$',
        online_status.OnlineStatusAPI.as_view(), name='online_status'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/comment/(?P<pk>\d+)/$',
        comments.CommentAPI.as_view(), name='comment'),
    urls.url(
        r'^variation/(?P<variation_id>\d+)/comment/(?P<pk>\d+)/voting/$',
        other.VotingAPI.as_view(), name='voting'),
]
