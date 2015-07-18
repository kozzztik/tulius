from django.utils.safestring import mark_safe
from .models import DataBlock

def datablocks(request):
    objs = DataBlock.objects.languaged()
    datablocks = {}
    for datablock in objs:
        if datablock.urls:
            urls = datablock.urls.split()
            urls = [url.strip() for url in urls]
            if not request.path in urls:
                continue
        elif datablock.exclude_urls:
            urls = datablock.exclude_urls.split()
            urls = [url.strip() for url in urls]
            if request.path in urls:
                continue
        datablocks[datablock.name] = mark_safe(datablock.full_text)
    return {
        'datablocks': datablocks,
        'request': request
    }