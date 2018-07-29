from djfw.flatpages.models import FlatPage


def flatpages(request):
    return {
        'flatpages': FlatPage.objects.filter(is_enabled=True),
        'request': request
    }
