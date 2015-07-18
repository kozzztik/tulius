from django.conf.urls import patterns, url
from .views import UserExceptions, ComplaintsView, SiteUpdates, SiteUpdatesFeed, issue_views
from djfw.bugtracker.views import VersionsAdminViews

class MyVersionsAdminViews(VersionsAdminViews):
    def read_right(self, model, user):
        return True
    
versions_views = MyVersionsAdminViews(app_name='bugs', base_template='bugs/base.html')

urlpatterns = patterns ('',
    url(r'^user_exceptions(?P<user_id>\d+)/$', UserExceptions.as_view(), name='user_exceptions'),
    url(r'^complaints/$', ComplaintsView.as_view(), name='complaints'),
    url(r'^site_updates/$', SiteUpdates.as_view(), name='site_updates'),
    url(r'^site_updates/feed/$', SiteUpdatesFeed(), name='updates_feed'),
) + issue_views.get_urls() + versions_views.get_urls() 