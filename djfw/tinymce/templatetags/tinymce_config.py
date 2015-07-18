from django.utils.safestring import mark_safe
from django.conf import settings
from django import template

register = template.Library()

@register.simple_tag
def tinymce_css():
    css_link = getattr(settings, 'TINYMCE_CSS', getattr(settings, 'MEDIA_URL', '/media/') + 
                       'css/tinymce.css')
    return mark_safe(css_link)