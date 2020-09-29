from django.conf import urls

from tulius.core.ckeditor import views


app_name = 'tulius.core.ckeditor'

urlpatterns = [
    urls.re_path(r'^images/$', views.Images.as_view(), name='images'),
    urls.re_path(r'^smiles/$', views.Smiles.as_view(), name='smiles'),
]
