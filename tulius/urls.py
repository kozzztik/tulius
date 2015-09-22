from django.conf.urls import patterns, include, url
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib import admin
from tulius.views import HomeView, StatisticsView
from django.conf import settings
from tulius import forum, gameforum
from djfw.flatpages.views import FlatpagesList
from .sitemap import sitemaps
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap.xml$', sitemaps_views.index, {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap, {'sitemaps': sitemaps}, name='sitemaps'),
    
    url(r'^accounts/', include('djfw.accounts.urls')),
    url(r'^tinymce/', include('djfw.tinymce.urls',  namespace='tinymce')),
    url(r'^wysibb/', include('djfw.wysibb.urls',  namespace='wysibb')),
    url(r'^news/', include('djfw.news.urls',  namespace='news')),
    url(r'^flatpages/$', FlatpagesList.as_view(),  name='flatpages'),
    url(r'^autocomplete/', include('djfw.autocomplete.urls',  namespace='autocomplete')),
    url(r'^bugtracker/', include('djfw.bugtracker.urls',  namespace='bugtracker')),
    url(r'^profiler/', include('djfw.profiler.urls',  namespace='profiler')),
    url(r'^installer/', include('djfw.installer.urls', namespace='installer')),
    
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^statistics/$', StatisticsView.as_view(), name='stats'),

    url(r'^players/', include('tulius.players.urls', namespace='players')),
    url(r'^profile/', include('tulius.profile.urls', namespace='profile')),
    url(r'^pm/', include('pm.urls', namespace='pm')),
    url(r'^games/', include('tulius.games.urls',  namespace='games')),
    url(r'^forums/', include(forum.site.urls)),
    url(r'^stories/', include('tulius.stories.urls',  namespace='stories')),
    url(r'^play/', include(gameforum.site.urls)),
    
    url(r'^bugs/', include('tulius.bugs.urls',  namespace='bugs')),
    url(r'^vk/', include('tulius.vk.urls',  namespace='vk')),
    url(r'^counters/', include('tulius.counters.urls',  namespace='counters')),
)

handler404 = 'tulius.views.error404'
handler500 = 'tulius.views.error500'

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )

from djfw.installer.signals import maintaince_finished, maintaince_started
from tulius.bugs.views import maint_updated
        

def set_locale(sender, **kwargs):
    import platform
    is_windows = platform.system() == 'Windows'
    if not is_windows:
        import locale
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

maintaince_finished.connect(maint_updated)
maintaince_started.connect(set_locale)

set_locale(None)

