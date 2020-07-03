import io
from django.core.files import uploadedfile

from tulius.forum import plugins
from djfw.wysibb import models
from djfw.wysibb import views as djfw_views


class Images(plugins.BaseAPIView):
    require_user = False

    def get_context_data(self, **kwargs):
        images = models.UploadedImage.objects.filter(
            user=self.user).order_by('-id')[:50]
        return {'images': [
            {
                'id': image.id,
                'file_name': image.filename,
                'url': image.image.url if image.image else None,
                'thumb': image.thumb.url if image.thumb else None,
            } for image in images
        ]}

    def put(self, request):
        uploaded = uploadedfile.InMemoryUploadedFile(
            io.BytesIO(request.body),
            'upload',
            request.GET['file_name'],
            content_type=request.GET['content_type'],
            size=len(request.body),
            charset=None
        )
        response = djfw_views.save_uploaded_image(
            request, uploaded, request.GET['file_name'])
        return {
            'id': response['id'],
            'file_name': response['file_name'],
            'url': response['image_link'],
            'thumb': response['thumb_link'],
        }
