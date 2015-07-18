from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^auth/', include('djfw.accounts.auth.urls', namespace='auth')),
    url(r'^registration/', include('djfw.accounts.registration.backends.default.urls')),
)