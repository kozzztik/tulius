from django.db.models.query_utils import Q
from django.utils import translation
from .models import TreePage

def treepages(request):
    lang = translation.get_language()
    query = Q(parent=None, is_enabled=True) & (Q(language=lang) | Q(language__isnull=True))
    return {
        'treepages': TreePage.objects.filter(query).order_by('position'),
        'request': request
    }