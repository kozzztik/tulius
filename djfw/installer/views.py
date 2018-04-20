from django import http
from django.shortcuts import get_object_or_404
from . import models


def download_backup(request, object_id):
    if request.user.is_anonymous:
        raise http.Http404()
    if not request.user.is_staff:
        raise http.Http404()
    backup = get_object_or_404(models.Backup, id=object_id)
    file_obj = open(backup.path(), 'rb')
    response = http.HttpResponse(file_obj, mimetype='application/x-gzip')
    response['Content-Disposition'] = 'filename=' + backup.file_name()
    return response
