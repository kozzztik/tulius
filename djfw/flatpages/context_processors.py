from djfw.flatpages.models import FlatPage
from django.db.models.query_utils import Q
from django.utils import translation

def flatpages(request):
	lang = translation.get_language()
	return {
		'flatpages': FlatPage.objects.filter(is_enabled=True),
		'request': request
	}