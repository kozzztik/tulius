import io

from django import dispatch
from django.db import transaction
from django.core import exceptions
from django.core.files import uploadedfile

from tulius.forum import core
from tulius.forum.threads import signals as thread_signals
from tulius.forum.comments import signals as comment_signals
from djfw.wysibb import models


@dispatch.receiver(thread_signals.before_create)
def before_create_thread(instance, data, view, **_kwargs):
    if instance.room:
        return
    html_data = data['media'].get('html')
    if html_data and view.user.is_superuser:
        instance.media['html'] = html_data


@dispatch.receiver(comment_signals.before_add)
def before_add_comment(comment, data, view, **_kwargs):
    html_data = data['media'].get('html')
    if (not html_data) or (not view.user.is_superuser):
        return
    if view.obj.first_comment_id == comment.id:
        comment.media['html'] = view.obj.media['html']
    else:
        comment.media['html'] = html_data


@dispatch.receiver(comment_signals.on_update)
def on_comment_update(comment, data, view, **_kwargs):
    if not view.user.is_superuser:
        return
    html_data = data['media'].get('html')
    orig_data = comment.media.get('html')
    if orig_data and not html_data:
        del comment.media['html']
    elif html_data:
        comment.media['html'] = html_data
    if view.obj.first_comment_id == comment.id:
        if (not html_data) and ('html' in view.obj.media):
            del view.obj.media['html']
        elif html_data:
            view.obj.media['html'] = html_data


class UploadFiles(core.BaseAPIView):
    require_user = False

    @staticmethod
    def file_to_json(uploaded_file):
        return {
            'id': uploaded_file.pk,
            'file_name': uploaded_file.filename,
            'url': uploaded_file.body.url,
        }

    def get_context_data(self, **kwargs):
        files = models.UploadedFile.objects.filter(
            user=self.user).order_by('-id')[:50]
        return {'files': [
            self.file_to_json(f) for f in files
        ]}

    @transaction.atomic
    def put(self, request):
        if not request.user.is_superuser:
            raise exceptions.PermissionDenied()
        file_name = request.GET['file_name']
        content_type = request.GET['content_type']
        uploaded = uploadedfile.InMemoryUploadedFile(
            io.BytesIO(request.body),
            'upload',
            file_name,
            content_type=content_type,
            size=len(request.body),
            charset=None
        )
        uploaded_file = models.UploadedFile(
            user=request.user,
            filename=file_name,
            file_size=len(request.body),
            mime=content_type
        )
        uploaded_file.save()
        uploaded_file.body.save(f'{uploaded_file.pk}_{file_name}', uploaded)
        uploaded_file.save()
        return self.file_to_json(uploaded_file)
