from django import template
from djfw.tinymce.bbcodes import bbcode_to_html

register = template.Library()

@register.filter
def bb_code(value):
    return bbcode_to_html(value)

