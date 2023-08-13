import os
import io
from mimetypes import guess_type

from django.http import HttpResponseBadRequest
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

from djfw.uploader import handle_upload
from djfw.common import generate_random_id
from tulius.stories.models import Illustration


MAX_ILLUSTRATION_SIZE = 20 * 1024 * 1024


def check_mime(request):
    filename = request.GET['qqfile']
    mime = guess_type(filename, True)[0]
    if mime[:5] != 'image':
        return HttpResponseBadRequest("Only image upload, not " + mime)
    if int(request.META['CONTENT_LENGTH']) > MAX_ILLUSTRATION_SIZE:
        return HttpResponseBadRequest("File too big")
    return None


ILLUSTRATION_THUMBNAIL = (100, 100)


# pylint: disable=too-many-arguments
def save_illustration(
        request, upload, filename, story, variation, illustration):
    """
    raw_data: if True, upfile is a HttpRequest object with raw post data
    as the file, rather than a Django UploadedFile from request.FILES
    """
    image = Image.open(upload)
    if not illustration:
        illustration = Illustration(
            story=story, variation=variation,
            name=os.path.splitext(filename)[0])
        illustration.save()
        name = generate_random_id(30)
    else:
        name = illustration.image.name
        if name:
            (name, _) = os.path.splitext(illustration.image.name)
        else:
            name = generate_random_id(30)
        illustration.delete_data()
    try:
        os.makedirs(os.path.split(illustration.file_path())[0])
    except:
        pass
    imageformat = getattr(settings, 'IMAGE_FORMAT', 'jpeg')
    image_content = io.BytesIO()
    image.save(image_content, format=imageformat)
    image_file = ContentFile(image_content.getvalue())
    illustration.image.save('%s.%s' % (name, imageformat,), image_file)
    image.thumbnail(ILLUSTRATION_THUMBNAIL, Image.ANTIALIAS)
    image_content = io.BytesIO()
    image.save(image_content, format=imageformat)
    image_file = ContentFile(image_content.getvalue())
    illustration.thumb.save('%s_thumb.%s' % (name, imageformat,), image_file)


def upload_illustration(request, story, variation, illustration):
    return handle_upload(
        request, save_illustration, story, variation, illustration)
