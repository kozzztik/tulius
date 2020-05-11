from io import BytesIO
from mimetypes import guess_type

from django import http
from django import urls
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
try:
    from PIL import Image
except ImportError:
    import Image

from djfw.uploader import handle_upload
from djfw.wysibb.templatetags import bbcodes
from .models import UploadedFile, UploadedImage
from .trans import transliterate


def save_uploaded_file(request, upload, filename):
    filename = transliterate(filename)
    uploaded_file = UploadedFile(
        user=request.user,
        filename=filename,
        file_size=len(upload),
        mime=(guess_type(filename, True)[0] or '')
    )
    uploaded_file.save()
    uploaded_file.body.save(str(uploaded_file.pk) + '_' + filename, upload)
    uploaded_file.save()
    return {'url': uploaded_file.body.url,
            'filename': uploaded_file.filename}


@login_required
def upload_file(request):
    return handle_upload(request, save_uploaded_file)


def save_uploaded_image(request, upload, filename):
    filename = transliterate(filename)
    uploaded_file = UploadedImage(
        user=request.user,
        filename=filename,
        file_size=len(upload),
        mime=(guess_type(filename, True)[0] or '')
    )

    uploaded_file.save()
    uploaded_file.image.save(str(uploaded_file.pk) + '_' + filename, upload)
    uploaded_file.save()
    uploaded_file.image.open('rb')
    image = Image.open(uploaded_file.image)

    thumb_size = getattr(settings, 'WYSIBB_THUMB_SIZE', (100, 100))
    thumb_format = getattr(settings, 'WYSIBB_THUMB_FORMAT', 'png')
    image.thumbnail(thumb_size, Image.ANTIALIAS)

    image_content = BytesIO()
    image.save(image_content, format=thumb_format)
    image_file = ContentFile(image_content.getvalue())
    uploaded_file.thumb.save(
        str(uploaded_file.pk) + '_' + filename, image_file)
    return {'status': 1,
            'msg': "OK",
            'image_link': uploaded_file.image.url,
            'thumb_link': uploaded_file.thumb.url}


@login_required
def upload_image(request):
    return handle_upload(request, save_uploaded_image)


def wysibb_options(request):
    ret_json = {
        'buttons': "bold,italic,underline,strike,|,img,video,myfile,link,"
                   "|,bullist,numlist,|,smilebox,|,fontcolor,fontsize,|,"
                   "quote,table,removeFormat",
        'smileList': [
            {
                'title': obj.name,
                'img': '<img src="{}" class="sm">'.format(obj.image.url),
                'bbcode': obj.text,
            } for obj in bbcodes.smiles
        ],
        'img_uploadurl': urls.reverse('wysibb:upload_image'),
        'minheight': '100',
        'allButtons': {
            'myfile': {
                'title': "Добавить файл",
                'buttonHTML':
                    '<span class="fonticon ve-tlb-img1">'
                    '<img src="/static/wysibb/filebutton.gif"/>'
                    '</span>',
                'modal': {
                    'title': "Добавить файл",
                    'width': "600px",
                    'tabs': [
                        {
                            'title': "",
                            'html':
                                '<form id="fupfileform" class="upload" '
                                'method="post" enctype="multipart/form-data">'
                                '<input id="fileupl" class="file" type="file" '
                                'name="img" /></form>'
                        }
                    ],
                    # should be replaced on recieve
                    'onSubmit': 'javascript:wysibb_file_load',
                },
                'transform': {
                    '<a href="{URL}">{FILENAME}</a>':
                        "[url={URL}]{FILENAME}[/url]",
                }
            },
        }
    }
    return http.JsonResponse(ret_json)
