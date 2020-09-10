from django.conf import urls

from tulius.profile import views


app_name = 'tulius.profile'


urlpatterns = [
    urls.re_path(
        r'^favorites/$',
        views.Index.as_view(),
        name='favorites'),
    urls.re_path(
        r'^stories/$', views.PlayerStoriesView.as_view(), name='stories'),
    urls.re_path(r'^games/$', views.PlayerGamesView.as_view(), name='games'),
    urls.re_path(
        r'^settings/$', views.PlayerSettingsView.as_view(), name='settings'),
    urls.re_path(r'^invites/$', views.InvitesView.as_view(), name='invites'),
    urls.re_path(
        r'^invite_accept(?P<invite_id>\d+)/$',
        views.PlayerInviteAcceptView.as_view(),
        name='invite_accept'),
    urls.re_path(
        r'^invite_decline(?P<invite_id>\d+)/$',
        views.PlayerInviteDeclineView.as_view(),
        name='invite_decline'),
    urls.re_path(
        r'^subscriptions/$', views.PlayerSubscriptionsView.as_view(),
        name='subscriptions'),
]
