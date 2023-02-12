from django import urls

from tulius.players import views
from tulius.players import avatar_upload


app_name = 'tulius.players'


urlpatterns = [
    urls.re_path(r'^$', views.PlayersListView.as_view(), name='index'),
    urls.re_path(
        r'^(?P<player_id>\d+)/$', views.PlayerDetailsView.as_view(),
        name='player_details'),
    urls.re_path(
        r'^(?P<player_id>\d+)/history/$', views.PlayerHistoryView.as_view(),
        name='player_history'),
    urls.re_path(
        r'^(?P<player_id>\d+)/played/$', views.PlayerUserProfileView.as_view(),
        name='player_played'),
    urls.re_path(
        r'^profile/$', views.PlayerProfileView.as_view(), name='profile'),
    urls.re_path(
        r'^profile/upload_avatar/$', avatar_upload.profile_upload_avatar,
        name='profile_upload_avatar'),
    # TODO: Not sure this pages still used.
    # url(
    #     r'^profile/files/$', PlayerUploadedFilesView.as_view(),
    #     name='profile_files'),
    urls.re_path(
        r'^profile/played/$', views.PlayerPlayedView.as_view(),
        name='profile_played'),
]
