from django.views.generic.simple import direct_to_template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, Http404
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from django.conf import settings
from djfw.uploader import handle_upload
from .models import Photo, PhotoAlbum
try:
    from PIL import Image
except ImportError:
    import Image
import os
import StringIO

def save_upload(request, upload, filename, album):
    name = os.path.splitext(filename)[0]
    uploaded_file = Photo(user=request.user, album=album, title=name)
    image = Image.open(upload)
    imageformat = getattr(settings, 'IMAGE_FORMAT', 'png')
    image_content = StringIO.StringIO()
    image.save(image_content, format=imageformat)
    image_file = ContentFile(image_content.getvalue())
    uploaded_file.file_length = image_file.size    
    uploaded_file.save()
    uploaded_file.image.save(str(uploaded_file.pk) + '_' + name + '.' + imageformat, image_file)

    image.thumbnail((150, 100), Image.ANTIALIAS)
    image_content = StringIO.StringIO()
    image.save(image_content, format=imageformat)
    image_file = ContentFile(image_content.getvalue())
    uploaded_file.thumbnail.save(str(uploaded_file.pk) + '_' + name + '.' + imageformat, image_file)
    uploaded_file.save()
    if not album.title_photo:
        album.title_photo = uploaded_file
        album.save()
    return {'url': uploaded_file.image.url, 
            'filename': uploaded_file.title}

@login_required
def upload_file(request, album_id):
    if not request.user.is_staff:
        raise Http404()
    try:
        album_id = int(album_id)
    except:
        raise Http404()
    album = get_object_or_404(PhotoAlbum, id=album_id)
    return handle_upload(request, save_upload, album)
