from django import template
from django.utils import html

from djfw.wysibb.models import Smile
from .bb_parser import bbcode_to_html

register = template.Library()

smiles = Smile.objects.all()


@register.filter
def bbcode(value):
    data = bbcode_to_html(html.escape(value))
    for smile in smiles:
        data = data.replace(
            smile.text, '<img class="sm" src="%s" title="%s" />' % (
                smile.image.url, smile.name))
    return data


@register.inclusion_tag('wysibb/smiles_list.html')
def bbcode_smiles_list():
    return {'smiles': smiles}
