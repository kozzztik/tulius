from django import urls

from tulius.core.autocomplete import views

app_name = 'tulius.core.autocomplete'

urlpatterns = [
    urls.re_path('user', views.autocomplete_user, name='user'),
    urls.re_path(
        r'^(?P<token>[\w-]+)/$', views.get_autocomplete, name='autocomplete'),
]
