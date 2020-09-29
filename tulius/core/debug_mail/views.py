import os
import datetime

from django import http
from django.views import generic
from django.conf import settings
from django.core import exceptions


class RecipientsAPI(generic.View):
    @staticmethod
    def get(request, *args, **_kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied()
        base_dir = settings.EMAIL_FILE_PATH
        query = request.GET.get('q')
        result = []
        for file_name in os.listdir(base_dir):
            path = os.path.join(base_dir, file_name)
            if os.path.isdir(path) and ((not query) or query in file_name):
                result.append({
                    'name': file_name,
                    'count': len(os.listdir(path))
                })
        return http.JsonResponse({'result': result})


class MailboxAPI(generic.View):
    @staticmethod
    def get(request, email, **_kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied()
        base_dir = os.path.join(settings.EMAIL_FILE_PATH, email)
        result = []
        for entry in os.scandir(path=base_dir):
            if entry.is_file():
                timestamp = entry.stat().st_mtime_ns
                result.append({
                    'name': entry.name,
                    'size': entry.stat().st_size,
                    'timestamp': timestamp,
                    'date': str(datetime.datetime.fromtimestamp(
                        timestamp / 1000000000))
                })
        result.sort(key=lambda x: x['timestamp'], reverse=True)
        return http.JsonResponse({'result': result[:100]})


class MailAPI(generic.View):
    @staticmethod
    def get(request, email, pk, **_kwargs):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied()
        file_name = os.path.join(settings.EMAIL_FILE_PATH, email, pk)
        f = open(file_name, 'rb')
        try:
            data = f.read()
        finally:
            f.close()
        return http.HttpResponse(data)
