import re

from django import template

from djfw.wysibb.models import Smile
from .bb_parser import bbcode_to_html

register = template.Library()

bad_tags = [
    re.compile(r'\<span(.*?)\>'), re.compile(r'\</span(.*?)\>'),
    re.compile(r'\<div(.*?)\>'), re.compile(r'\</div(.*?)\>'),
    re.compile(r'\<font(.*?)\>'), re.compile(r'\</font(.*?)\>')
]

smiles = Smile.objects.all()


@register.filter
def bbcode(value):
    for p in bad_tags:
        value = p.sub('', value)
    data = bbcode_to_html(value)
    for smile in smiles:
        data = data.replace(
            smile.text, '<img class="sm" src="%s" title="%s" />' % (
                smile.image.url, smile.name))
    value = value.replace('<', '&lt;').replace('>', '&gt;')
    return data


@register.inclusion_tag('wysibb/smiles_list.html')
def bbcode_smiles_list():
    return {'smiles': smiles}
