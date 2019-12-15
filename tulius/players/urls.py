from django.conf import urls

from tulius.players import views
from tulius.players import avatar_upload


app_name = 'tulius.players'


urlpatterns = [
    urls.url(r'^$', views.PlayersListView.as_view(), name='index'),
    urls.url(
        r'^(?P<player_id>\d+)/$', views.PlayerDetailsView.as_view(),
        name='player_details'),
    urls.url(
        r'^(?P<player_id>\d+)/history/$', views.PlayerHistoryView.as_view(),
        name='player_history'),
    urls.url(
        r'^(?P<player_id>\d+)/played/$', views.PlayerUserProfileView.as_view(),
        name='player_played'),
    urls.url(r'^profile/$', views.PlayerProfileView.as_view(), name='profile'),
    urls.url(
        r'^profile/upload_avatar/$', avatar_upload.profile_upload_avatar,
        name='profile_upload_avatar'),
    # TODO: Not sure this pages still used.
    # url(
    #     r'^profile/files/$', PlayerUploadedFilesView.as_view(),
    #     name='profile_files'),
    urls.url(
        r'^profile/played/$', views.PlayerPlayedView.as_view(),
        name='profile_played'),
]
