import io
from mimetypes import guess_type
import os

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image

from tulius.stories.models import AVATAR_SIZES, AVATAR_SAVE_SIZE
from djfw.uploader import handle_upload


def save_upload(request, upload, filename, user):
    """
    raw_data: if True, upfile is a HttpRequest object with raw post data
    as the file, rather than a Django UploadedFile from request.FILES
    """
    check_mime(request, filename)
    image = Image.open(upload)
    image.thumbnail(AVATAR_SAVE_SIZE, Image.ANTIALIAS)
    imageformat = getattr(settings, 'IMAGE_FORMAT', 'jpeg')
    image_content = io.BytesIO()
    image.save(image_content, format=imageformat)
    image_file = ContentFile(image_content.getvalue())
    if user.avatar:
        user.avatar.delete()
    user.avatar.save(str(user.pk)+'.' + imageformat, image_file)
    path = user.avatar.path
    path = os.path.split(path)[0]
    for size in AVATAR_SIZES:
        small_image = Image.open(user.avatar.path)
        small_image.thumbnail(size, Image.ANTIALIAS)
        filename = "%s_%sx%s.%s" % (user.pk, size[0], size[1], imageformat)
        filepath = os.path.join(path, filename)
        small_image.save(filepath, imageformat.upper())
    return {'url': 'http://' + request.META['HTTP_HOST'] + user.avatar.url}


MAX_AVATAR_SIZE = 10 * 1024 * 1024


def check_mime(request, filename):
    mime = guess_type(filename, True)[0]
    if mime[:5] != 'image':
        raise Exception("Only image upload, not " + mime)
    if int(request.META['CONTENT_LENGTH']) > MAX_AVATAR_SIZE:
        raise Exception("File too big")


@login_required
def profile_upload_avatar(request):
    return handle_upload(request, save_upload, request.user)
