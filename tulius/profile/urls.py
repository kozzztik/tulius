from django.conf import urls

from tulius.profile import views


app_name = 'tulius.profile'


urlpatterns = [
    urls.url(
        r'^favorites/$',
        views.Index.as_view(),
        name='favorites'),
    urls.url(r'^stories/$', views.PlayerStoriesView.as_view(), name='stories'),
    urls.url(r'^games/$', views.PlayerGamesView.as_view(), name='games'),
    urls.url(
        r'^settings/$', views.PlayerSettingsView.as_view(), name='settings'),
    urls.url(r'^invites/$', views.InvitesView.as_view(), name='invites'),
    urls.url(
        r'^invite_accept(?P<invite_id>\d+)/$',
        views.PlayerInviteAcceptView.as_view(),
        name='invite_accept'),
    urls.url(
        r'^invite_decline(?P<invite_id>\d+)/$',
        views.PlayerInviteDeclineView.as_view(),
        name='invite_decline'),
    urls.url(
        r'^subscriptions/$', views.PlayerSubscriptionsView.as_view(),
        name='subscriptions'),
]
