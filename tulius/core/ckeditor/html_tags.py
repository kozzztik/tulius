from djfw.wysibb.templatetags import bb_parser
from djfw.wysibb.templatetags import bbcodes


class Tag:
    tag_name = None
    attrs = None
    parent = None
    childs = None
    start_end_tag = False
    start_pos = None
    end_pos = None
    content_start = None
    content_end = None

    def __init__(self, parent, tag_name, attrs):
        if parent:
            parent.childs.append(self)
        self.parent = parent
        self.tag_name = tag_name
        self.attrs = dict(attrs)
        self.childs = []

    def convert_internal(self, data_str):
        pos = self.content_start
        for child in self.childs:
            if child.start_pos > pos:
                yield data_str[pos:child.start_pos]
            yield from child.convert(data_str)
            pos = child.end_pos
        if pos < self.content_end:
            yield data_str[pos:self.content_end]

    def convert(self, data_str):
        yield from self.convert_internal(data_str)


class SimpleTag(Tag):
    override_tag = None

    def convert(self, data_str):
        yield '[{}]'.format(self.override_tag or self.tag_name)
        yield from self.convert_internal(data_str)
        yield '[/{}]'.format(self.override_tag or self.tag_name)


class BoldTag(SimpleTag):
    override_tag = 'b'


class ItalicTag(SimpleTag):
    override_tag = 'i'


class BrTag(Tag):
    def convert(self, data_str):
        yield '\n'


class ListItemTag(Tag):
    def convert(self, data_str):
        yield '[*]'
        yield from self.convert_internal(data_str)
        yield '\n'


class ListTag(Tag):
    def convert(self, data_str):
        yield '[list=1]' if self.tag_name == 'ol' else '[list]'
        yield from self.convert_internal(data_str)
        yield '[/list]'


class FontTag(Tag):
    def convert(self, data_str):
        color = self.attrs.get('color', '')
        if not bb_parser.check_color(color):
            yield from super(FontTag, self).convert(data_str)
        else:
            yield '[color={}]'.format(color)
            yield from self.convert_internal(data_str)
            yield '[/color]'


class SpanTag(Tag):
    font_sizes = {
        '200%': 200, '150%': 150, '100%': 100, '85%': 85, 'x-small': 50}

    def get_styles(self):
        styles = {}
        entries = self.attrs.get('style', '').split(';')
        for entry in entries:
            params = entry.split(':', 1)
            if len(params) != 2:
                continue
            key = params[0].strip()
            value = params[1].strip()
            if key == 'color' and bb_parser.check_color(value):
                styles['color'] = value
            elif key == 'font-size' and value in self.font_sizes.keys():
                styles['size'] = self.font_sizes[value]
        return styles

    def convert(self, data_str):
        styles = self.get_styles()
        if 'color' in styles:
            yield '[color={}]'.format(styles['color'])
        if 'size' in styles:
            yield '[size={}]'.format(styles['size'])
        yield from self.convert_internal(data_str)
        if 'size' in styles:
            yield '[/size]'
        if 'color' in styles:
            yield '[/color]'


class BlockquoteTag(SimpleTag):
    override_tag = 'quote'


class ATag(Tag):
    def convert(self, data_str):
        url = self.attrs.get('href', '')
        url = url.replace(']', '')
        if url:
            yield '[url={}]'.format(url)
        yield from self.convert_internal(data_str)
        if url:
            yield '[/url]'


class ImgTag(Tag):
    def is_smile(self):
        title = self.attrs.get('title')
        url = bbcodes.smiles.smile_dict().get(title)
        return title if url else None

    def convert(self, data_str):
        smile = self.is_smile()
        if smile:
            yield smile
        else:
            url = self.attrs.get('src', '').replace(']', '')
            alt = self.attrs.get('alt', '').replace(']', '')
            if url:
                yield '[img={}]{}[/img]'.format(url, alt)


class PTag(Tag):
    def convert(self, data_str):
        yield from self.convert_internal(data_str)
        yield '\n'


tag_types = {
    'em': ItalicTag,
    'i': ItalicTag,
    'b': BoldTag,
    'strong': BoldTag,
    'u': SimpleTag,
    's': SimpleTag,
    'big': SimpleTag,
    'small': SimpleTag,
    'table': SimpleTag,
    'tr': SimpleTag,
    'td': SimpleTag,
    'br': BrTag,
    'ol': ListTag,
    'ul': ListTag,
    'li': ListItemTag,
    'font': FontTag,
    'span': SpanTag,
    'blockquote': BlockquoteTag,
    'a': ATag,
    'img': ImgTag,
    'p': PTag,
}
