from django.apps import apps
from django.conf import settings
from django.conf.urls import include, url
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib import admin

from tulius.views import HomeView, StatisticsView
from djfw.flatpages.views import FlatpagesList
from djfw.installer.signals import maintaince_started
from .sitemap import sitemaps

admin.autodiscover()

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(
        r'^sitemap.xml$', sitemaps_views.index,
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(
        r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap,
        {'sitemaps': sitemaps}, name='sitemaps'),
    
    url(r'^tinymce/', include('djfw.tinymce.urls',  namespace='tinymce')),
    url(r'^wysibb/', include('djfw.wysibb.urls',  namespace='wysibb')),
    url(r'^news/', include('djfw.news.urls',  namespace='news')),
    url(r'^flatpages/$', FlatpagesList.as_view(),  name='flatpages'),
    url(
        r'^autocomplete/',
        include('djfw.autocomplete.urls', namespace='autocomplete')),
    url(r'^profiler/', include('djfw.profiler.urls',  namespace='profiler')),
    url(r'^installer/', include('djfw.installer.urls', namespace='installer')),
    
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^statistics/$', StatisticsView.as_view(), name='stats'),

    url(r'^accounts/', include('tulius.login.urls', namespace='auth')),
    url(r'^players/', include('tulius.players.urls', namespace='players')),
    url(r'^profile/', include('tulius.profile.urls', namespace='profile')),
    url(r'^pm/', include('pm.urls', namespace='pm')),
    url(r'^games/', include('tulius.games.urls',  namespace='games')),
    url(
        r'^forums/',
        include(apps.get_app_config('forum').site.urls)),
    url(r'^stories/', include('tulius.stories.urls',  namespace='stories')),
    url(r'^play/', include(apps.get_app_config('gameforum').site.urls)),
    
    url(r'^vk/', include('tulius.vk.urls',  namespace='vk')),
    url(r'^counters/', include('tulius.counters.urls',  namespace='counters')),
]

handler404 = 'tulius.views.error404'
handler500 = 'tulius.views.error500'

if settings.DEBUG:
    urlpatterns += [
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        (r'^static/(?P<path>.*)$', 'django.contrib.staticfiles.views.serve')
    ]


def set_locale(sender, **kwargs):
    import platform
    is_windows = platform.system() == 'Windows'
    if not is_windows:
        import locale
        locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


maintaince_started.connect(set_locale)

set_locale(None)
