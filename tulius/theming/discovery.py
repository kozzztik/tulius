from django.conf import settings
import os

def get_available_themes():
    """
    Discover themes available in filesystem
    """
    list = os.listdir(settings.THEMING_ROOT)
    list.sort()
    return list

def get_current_theme(request):
    """
    Return current cookie-stored theme name or default name
    """
    return request.COOKIES['theme'] if 'theme' in request.COOKIES else settings.DEFAULT_THEME