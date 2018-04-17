from django.conf.urls import url
from .views import *

app_name = 'tulius.profile'


urlpatterns = [
    url(r'^favorites/$', PlayerFavoritesView.as_view(), name='favorites'),
    url(r'^stories/$', PlayerStoriesView.as_view(), name='stories'),
    url(r'^games/$', PlayerGamesView.as_view(), name='games'),
    url(r'^settings/$', PlayerSettingsView.as_view(), name='settings'),
    url(r'^invites/$', InvitesView.as_view(), name='invites'),
    url(
        r'^invite_accept(?P<invite_id>\d+)/$',
        PlayerInviteAcceptView.as_view(),
        name='invite_accept'),
    url(
        r'^invite_decline(?P<invite_id>\d+)/$',
        PlayerInviteDeclineView.as_view(),
        name='invite_decline'),
    url(
        r'^subscriptions/$', PlayerSubscriptionsView.as_view(),
        name='subscriptions'),
]
