from django.conf import settings
from discovery import get_available_themes, get_current_theme

def themes(request):
    return {
        'THEMING_URL': settings.THEMING_URL,
        'current_theme': get_current_theme(request),
        'themes': get_available_themes(),
        'request': request
    }