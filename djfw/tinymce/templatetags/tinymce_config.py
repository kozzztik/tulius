from django.utils.safestring import mark_safe
from django.conf import settings
from django import template

register = template.Library()


@register.simple_tag
def tinymce_css():
    default = getattr(settings, 'MEDIA_URL', '/media/') + 'css/tinymce.css'
    css_link = getattr(settings, 'TINYMCE_CSS', default)
    return mark_safe(css_link)
