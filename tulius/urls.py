from django.conf import settings
from django.conf import urls
from django.contrib.sitemaps import views as sitemaps_views
from django.contrib import admin
from django.conf.urls.static import static

from djfw.flatpages.views import FlatpagesList
from tulius import views
from tulius.forum.other import sitemap as forum_sitemap
from tulius.gameforum.other import sitemap as game_forum_sitemap

from tulius.sitemap import sitemaps

admin.autodiscover()


def trigger_error(_):
    raise ZeroDivisionError()


urlpatterns = [
    urls.re_path(r'^sentry-debug/$', trigger_error),
    urls.re_path(r'^i18n/', urls.include('django.conf.urls.i18n')),
    urls.re_path(
        r'^admin/doc/', urls.include('django.contrib.admindocs.urls')),
    urls.re_path(r'^admin/', admin.site.urls),
    urls.re_path(
        r'^sitemap.xml$', sitemaps_views.index,
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    urls.re_path(
        r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap,
        {'sitemaps': sitemaps}, name='sitemaps'),

    urls.re_path(
        r'^tinymce/', urls.include('djfw.tinymce.urls', namespace='tinymce')),
    urls.re_path(
        r'^wysibb/', urls.include('djfw.wysibb.urls', namespace='wysibb')),
    urls.re_path(r'^news/', urls.include('djfw.news.urls', namespace='news')),
    urls.re_path(r'^flatpages/$', FlatpagesList.as_view(), name='flatpages'),
    urls.re_path(
        r'^autocomplete/', urls.include(
            'tulius.core.autocomplete.urls', namespace='autocomplete')),
    urls.re_path(
        r'^profiler/', urls.include(
            'djfw.profiler.urls', namespace='profiler')),
    urls.re_path(
        r'^installer/', urls.include(
            'djfw.installer.urls', namespace='installer')),

    urls.re_path(r'^$', views.HomeView.as_view(), name='home'),
    urls.re_path(
        r'^celery_status/$', views.IndexVue.as_view(), name='celery_status'),
    urls.re_path(
        r'^api/celery_status/$', views.CeleryStatusAPI.as_view(),
        name='celery_status_api'),
    urls.re_path(
        r'^api/flatpages/$', views.ArticlesAPI.as_view(),
        name='flatpages_api'),
    urls.re_path(
        r'^api/app_settings/$', views.AppSettingsAPI.as_view(),
        name='app_settings'),
    urls.re_path(
        r'^api/debug_mail/', urls.include(
            'tulius.core.debug_mail.urls', namespace='debug_mail_api')),
    urls.re_path(r'^debug_mail/', views.IndexVue.as_view(), name='debug_mail'),

    urls.re_path(
        r'^statistics/$', views.StatisticsView.as_view(), name='stats'),

    urls.re_path(
        r'^accounts/', urls.include('tulius.login.urls', namespace='auth')),
    urls.re_path(
        r'^players/', urls.include(
            'tulius.players.urls', namespace='players')),
    urls.re_path(
        r'^profile/', urls.include(
            'tulius.profile.urls', namespace='profile')),
    urls.re_path(
        r'^api/profile/',
        urls.include('tulius.profile.api_urls', namespace='profile_api')),
    urls.re_path(
        r'^pm/', urls.include('tulius.pm.urls', namespace='pm')),
    urls.re_path(
        r'^games/', urls.include('tulius.games.urls', namespace='games')),
    urls.re_path(
        r'^forums/sitemap\.xml$',
        sitemaps_views.sitemap,
        {'sitemaps': forum_sitemap.ForumSitemap.sitemaps()},
        name='forum_sitemap'),
    urls.re_path(r'^forums/', views.IndexVue.as_view()),
    urls.re_path(
        r'^api/forum/', urls.include(
            'tulius.forum.urls', namespace='forum_api')),
    urls.re_path(
        r'^api/ckeditor/',
        urls.include('tulius.core.ckeditor.urls', namespace='ckeditor')),
    urls.re_path(
        r'^stories/', urls.include(
            'tulius.stories.urls', namespace='stories')),
    urls.re_path(
        r'^play/sitemap\.xml$',
        sitemaps_views.sitemap,
        {'sitemaps': game_forum_sitemap.GameForumSitemap.sitemaps()},
        name='game_forum_sitemap'),
    urls.re_path(r'^play/', views.IndexVue.as_view()),
    urls.re_path(
        r'^api/game_forum/', urls.include(
            'tulius.gameforum.urls', namespace='game_forum_api')),

    urls.re_path(r'^vk/', urls.include('tulius.vk.urls', namespace='vk')),
    urls.re_path(
        r'^counters/', urls.include(
            'tulius.counters.urls', namespace='counters')),
]

handler404 = 'tulius.views.error404'
handler500 = 'tulius.views.error500'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
