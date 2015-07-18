from django.utils.timezone import now
from django.utils import translation
from .models import NewsItem

def flatpages(request):
	lang = translation.get_language()
	return {
		'news': NewsItem.objects.filter(is_published=True, published_at__lt=now(), language=lang).order_by('-published_at')[:3],
		'request': request
	}