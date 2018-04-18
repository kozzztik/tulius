import json
from mimetypes import guess_type

from django.views.generic import TemplateView, View
from django.http import Http404
from django.conf import settings
from django.db import transaction

from djfw.uploader import handle_upload
from .models import Emotion, FileUpload


class Smiles(TemplateView):
    template_name = 'tinymce/smiles/tiny_mce_smiles.haml'
    
    def get_context_data(self, **kwargs):
        emotions = Emotion.objects.all()
        if not emotions:
            path = settings.STATIC_ROOT + '/tinymce/list.json'
            f = open(path, 'r')
            emotions_list = json.load(f)
            with transaction.commit_on_success():
                for emotion in emotions_list:
                    emotion_obj = Emotion(
                        name=emotion['name'],
                        text=emotion['text'],
                        filename=emotion['filename'])
                    emotion_obj.save()
            emotions = Emotion.objects.all()
        emotions_list = {}
        new_emotions = []
        for emotion in emotions:
            if not (emotion.filename in emotions_list):
                emotions_list[emotion.filename] = emotion
                new_emotions += [emotion]
        emotions = []
        for i in range(0, len(new_emotions)/10 + 1):
            emotions += [new_emotions[10*i:10*i+10]]
        return {'emotions': emotions}


class Uploaded_files(TemplateView):
    template_name = 'tinymce/plugins/file_upload.haml'
    
    def get_context_data(self, **kwargs):
        if not self.request.user.is_anonymous:
            all_files = FileUpload.objects.filter(
                user=self.request.user).order_by('-id')[:15]
            all_files = [afile for afile in all_files if afile.body]
        else:
            all_files = []
        files = []
        for i in range(0, len(all_files)/5 + 1):
            files += [all_files[5*i:5*i+5]]
        return {'files': files}


def save_upload(request, upload, filename):
    uploaded_file = FileUpload(
        user=request.user,
        filename=filename,
        file_length=len(upload),
        mime=guess_type(filename, True)[0])
    if uploaded_file.mime is None:
        uploaded_file.mime = ''
    uploaded_file.save()
    uploaded_file.body.save(str(uploaded_file.pk) + '_' + filename, upload)
    uploaded_file.save()
    return {'url': uploaded_file.body.url, 
            'filename': uploaded_file.filename, 
            'image': uploaded_file.is_image()}


class Upload_file(View):
    def post(self, request, *args, **kwargs):
        if request.user.is_staff:
            return handle_upload(request, save_upload)
        else:
            raise Http404()
