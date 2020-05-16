from django import http
from django import views

from django.conf import settings
from django.core import exceptions
from djfw.wysibb import views as djfw_views
from djfw.wysibb import models


class Images(views.View):
    def get(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            raise exceptions.PermissionDenied()
        return http.JsonResponse({})

    def post(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            raise exceptions.PermissionDenied()
        response = djfw_views.save_uploaded_image(
            request, request.FILES['upload'], request.FILES['upload'].name)
        return http.JsonResponse({
            'uploaded': 1,
            'fileName': response['file_name'],
            'url': response['image_link'],
        })


class Smiles(views.View):
    def get(self, request, *args, **kwargs):
        smiles = models.Smile.objects.all()
        base_url = settings.MEDIA_URL + models.Smile.image.field.upload_to
        return http.JsonResponse({
            'base_url': base_url,
            'smiles': [{
                'text': smile.text,
                'file_name': smile.image.url.replace(base_url, ''),
            } for smile in smiles],
        })
