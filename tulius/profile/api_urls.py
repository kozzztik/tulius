from django.conf import urls

from tulius.profile import views


app_name = 'tulius.profile'

urlpatterns = [
    urls.url(r'^$', views.UserProfileAPIView.as_view(), name='profile'),
]
