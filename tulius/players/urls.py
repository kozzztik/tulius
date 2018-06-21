from django.conf.urls import url

from .views import *
from .avatar_upload import profile_upload_avatar


app_name = 'tulius.players'


urlpatterns = [
    url(r'^$', PlayersListView.as_view(), name='index'),
    url(
        r'^(?P<player_id>\d+)/$', PlayerDetailsView.as_view(),
        name='player_details'),
    url(
        r'^(?P<player_id>\d+)/history/$', PlayerHistoryView.as_view(),
        name='player_history'),
    url(
        r'^(?P<player_id>\d+)/played/$', PlayerUserProfileView.as_view(),
        name='player_played'),
    # TODO: Not sure this pages still used.
    url(r'^profile/$', PlayerProfileView.as_view(), name='profile'),
    url(
        r'^profile/upload_avatar/$', profile_upload_avatar,
        name='profile_upload_avatar'),
    url(
        r'^profile/files/$', PlayerUploadedFilesView.as_view(),
        name='profile_files'),
    url(
        r'^profile/played/$', PlayerPlayedView.as_view(),
        name='profile_played'),
]
