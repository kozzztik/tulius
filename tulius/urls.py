from django.conf import settings
from django.conf.urls import include, url, re_path
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib import admin
from django.conf.urls.static import static

from djfw.flatpages.views import FlatpagesList
from tulius import views
from tulius.forum.other import sitemap as forum_sitemap
from tulius.gameforum.other import sitemap as game_forum_sitemap

from .sitemap import sitemaps

admin.autodiscover()


def trigger_error(request):
    raise ZeroDivisionError()


urlpatterns = [
    re_path(r'^sentry-debug/$', trigger_error),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', admin.site.urls),
    url(
        r'^sitemap.xml$', sitemaps_views.index,
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    url(
        r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap,
        {'sitemaps': sitemaps}, name='sitemaps'),

    url(r'^tinymce/', include('djfw.tinymce.urls', namespace='tinymce')),
    url(r'^wysibb/', include('djfw.wysibb.urls', namespace='wysibb')),
    url(r'^news/', include('djfw.news.urls', namespace='news')),
    url(r'^flatpages/$', FlatpagesList.as_view(), name='flatpages'),
    url(
        r'^autocomplete/',
        include('tulius.core.autocomplete.urls', namespace='autocomplete')),
    url(r'^profiler/', include('djfw.profiler.urls', namespace='profiler')),
    url(r'^installer/', include('djfw.installer.urls', namespace='installer')),

    url(r'^$', views.HomeView.as_view(), name='home'),
    url(r'^celery_status/$', views.IndexVue.as_view(),
        name='celery_status'),
    url(r'^api/celery_status/$', views.CeleryStatusAPI.as_view(),
        name='celery_status_api'),
    url(r'^api/flatpages/$', views.ArticlesAPI.as_view(),
        name='flatpages_api'),
    url(r'^api/app_settings/$', views.AppSettingsAPI.as_view(),
        name='app_settings'),

    url(r'^statistics/$', views.StatisticsView.as_view(), name='stats'),

    url(r'^accounts/', include('tulius.login.urls', namespace='auth')),
    url(r'^players/', include('tulius.players.urls', namespace='players')),
    url(r'^profile/', include('tulius.profile.urls', namespace='profile')),
    url(
        r'^api/profile/',
        include('tulius.profile.api_urls', namespace='profile_api')),
    url(r'^pm/', include('tulius.pm.urls', namespace='pm')),
    url(r'^games/', include('tulius.games.urls', namespace='games')),
    url(
        r'^forums/sitemap\.xml$',
        sitemaps_views.sitemap,
        {'sitemaps': forum_sitemap.ForumSitemap.sitemaps()},
        name='forum_sitemap'),
    url(r'^forums/', views.IndexVue.as_view()),
    url(r'^api/forum/', include('tulius.forum.urls', namespace='forum_api')),
    url(
        r'^api/ckeditor/',
        include('tulius.core.ckeditor.urls', namespace='ckeditor')),
    url(r'^stories/', include('tulius.stories.urls', namespace='stories')),
    url(
        r'^play/sitemap\.xml$',
        sitemaps_views.sitemap,
        {'sitemaps': game_forum_sitemap.GameForumSitemap.sitemaps()},
        name='game_forum_sitemap'),
    url(r'^play/', views.IndexVue.as_view()),
    url(r'^api/game_forum/',
        include('tulius.gameforum.urls', namespace='game_forum_api')),

    url(r'^vk/', include('tulius.vk.urls', namespace='vk')),
    url(r'^counters/', include('tulius.counters.urls', namespace='counters')),
]

handler404 = 'tulius.views.error404'
handler500 = 'tulius.views.error500'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
