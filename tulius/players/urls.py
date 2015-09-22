from django.conf.urls import patterns, url
from .views import *
from .avatar_upload import profile_upload_avatar
from tulius.bugs.views import UserExceptions

urlpatterns = patterns('',
    url(r'^$', PlayersListView.as_view(), name='index'),
    url(r'^(?P<player_id>\d+)/$', PlayerDetailsView.as_view(), name='player_details'),
    url(r'^(?P<player_id>\d+)/exceptions/$', 
        UserExceptions.as_view(template_name='players/exceptions.haml', pk_url_kwarg='player_id'), 
        name='player_exceptions'),

    url(r'^(?P<player_id>\d+)/send/$', PlayerSendMessageView.as_view(), name='player_send_message'),
    url(r'^(?P<player_id>\d+)/history/$', PlayerHistoryView.as_view(), name='player_history'),
    url(r'^(?P<player_id>\d+)/played/$', PlayerUserProfileView.as_view(), name='player_played'),
    
    url(r'^profile/$', PlayerProfileView.as_view(), name='profile'),
    url(r'^profile/upload_avatar/$', profile_upload_avatar, name='profile_upload_avatar'),
    url(r'^profile/files/$', PlayerUploadedFilesView.as_view(), name='profile_files'),
    url(r'^profile/played/$', PlayerPlayedView.as_view(), name='profile_played'),
)