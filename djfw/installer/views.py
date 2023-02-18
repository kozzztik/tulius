from django import http
from django.shortcuts import get_object_or_404
from . import models


def download_backup(request, object_id):
    if request.user.is_anonymous:
        raise http.Http404()
    if not request.user.is_staff:
        raise http.Http404()
    backup = get_object_or_404(models.Backup, id=object_id)
    return http.FileResponse(
        open(backup.path(), 'rb'), as_attachment=True,
        filename=backup.file_name(), content_type='application/x-gzip')
