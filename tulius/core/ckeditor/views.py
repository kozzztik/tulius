from django import http
from django import views

from django.core import exceptions
from djfw.wysibb import views as djfw_views


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
