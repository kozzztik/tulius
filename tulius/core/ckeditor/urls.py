from django.conf import urls

from tulius.core.ckeditor import views


app_name = 'tulius.core.ckeditor'

urlpatterns = [
    urls.url(r'^images/$', views.Images.as_view(), name='images'),
    urls.url(r'^smiles/$', views.Smiles.as_view(), name='smiles'),
]
