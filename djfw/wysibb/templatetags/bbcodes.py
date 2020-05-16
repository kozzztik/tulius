from django import template
from django.utils import html

from djfw.wysibb.models import Smile
from .bb_parser import bbcode_to_html

register = template.Library()


class Smiles:
    _smile_dict = None
    _smile_list = None

    def smile_dict(self):
        if self._smile_dict is None:
            self._smile_dict = {
                smile.text: smile.image.url for smile in self.get_list()}
        return self._smile_dict

    def get_list(self):
        if self._smile_list is None:
            self._smile_list = list(Smile.objects.all())
        return self._smile_list


smiles = Smiles()


@register.filter
def bbcode(value):
    data = bbcode_to_html(html.escape(value))
    for smile in smiles.get_list():
        data = data.replace(
            smile.text, '<img class="sm" src="%s" title="%s" />' % (
                smile.image.url, smile.name))
    return data


@register.inclusion_tag('wysibb/smiles_list.html')
def bbcode_smiles_list():
    return {'smiles': smiles.get_list()}
