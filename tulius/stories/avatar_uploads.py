import os
import io
from mimetypes import guess_type

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image

from djfw.uploader import handle_upload
from tulius.stories.models import AvatarAlternative
from .models import Avatar, AVATAR_SIZES, AVATAR_SAVE_SIZE
from .story_edit_views import get_story


MAX_AVATAR_SIZE = 10 * 1024 * 1024


def save_upload(request, upload, filename, story, avatar):
    """
    raw_data: if True, upfile is a HttpRequest object with raw post data
    as the file, rather than a Django UploadedFile from request.FILES
    """
    image = Image.open(upload)
    if (image.size[0] > AVATAR_SAVE_SIZE[0]) or (
            image.size[1] > AVATAR_SAVE_SIZE[1]):
        image.thumbnail(AVATAR_SAVE_SIZE, Image.ANTIALIAS)
    imageformat = getattr(settings, 'IMAGE_FORMAT', 'jpeg')
    image_content = io.BytesIO()
    image.save(image_content, format=imageformat)
    image_file = ContentFile(image_content.getvalue())
    if not avatar:
        avatar = Avatar(story=story, name=os.path.splitext(filename)[0])
        avatar.save()
    else:
        avatar.delete_data()
    avatar.image.save(str(avatar.pk) + '.' + imageformat, image_file)
    avatar.save()
    for size in AVATAR_SIZES:
        alternative = AvatarAlternative(
            avatar=avatar, height=size[0], width=size[1])
        alternative.save()
        small_image = Image.open(avatar.image.path)
        small_image.thumbnail(size, Image.ANTIALIAS)
        image_content = io.BytesIO()
        small_image.save(image_content, format=imageformat)
        image_file = ContentFile(image_content.getvalue())
        filepath = "%s-%sx%s.%s" % (avatar.pk, size[0], size[1], imageformat)
        alternative.image.save(filepath, image_file)


def check_mime(request):
    filename = request.GET['qqfile']
    mime = guess_type(filename, True)[0]
    if mime[:5] != 'image':
        return HttpResponseBadRequest("Only image upload, not " + mime)
    if int(request.META['CONTENT_LENGTH']) > MAX_AVATAR_SIZE:
        return HttpResponseBadRequest("File too big")
    return None


@login_required
def edit_story_avatar_upload(request, story_id):
    """
    Edit story view - Uploading avatar view
    """
    story = get_story(story_id, request.user)
    res = check_mime(request)
    if res:
        return res
    return handle_upload(request, save_upload, story, None)


@login_required
def edit_story_avatar_reload(request, avatar_id):
    """
    Edit story view - Uploading avatar view
    """
    try:
        avatar_id = int(avatar_id)
    except ValueError as exc:
        raise Http404() from exc
    avatar = get_object_or_404(Avatar, id=avatar_id)
    story = get_story(avatar.story.id, request.user)
    res = check_mime(request)
    if res:
        return res
    return handle_upload(request, save_upload, story, avatar)
