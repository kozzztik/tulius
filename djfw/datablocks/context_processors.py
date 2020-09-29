from django.utils.safestring import mark_safe

from djfw.datablocks import models


def datablocks(request):
    objs = models.DataBlock.objects.languaged()
    blocks = {}
    for datablock in objs:
        if datablock.urls:
            urls = datablock.urls.split()
            urls = [url.strip() for url in urls]
            if request.path not in urls:
                continue
        elif datablock.exclude_urls:
            urls = datablock.exclude_urls.split()
            urls = [url.strip() for url in urls]
            if request.path in urls:
                continue
        blocks[datablock.name] = mark_safe(datablock.full_text)
    return {
        'datablocks': blocks,
        'request': request
    }
