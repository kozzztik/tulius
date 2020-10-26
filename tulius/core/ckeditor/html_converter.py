import typing
from html import parser

from tulius.core.ckeditor import html_tags


class HtmlConverter(parser.HTMLParser):
    root: typing.Optional[html_tags.Tag] = None
    current_tag: typing.Optional[html_tags.Tag] = None
    new_tag: typing.Optional[html_tags.Tag] = None
    closed_tag_name: typing.Optional[str] = None

    def error(self, message):
        pass  # pragma: no cover

    def parse_starttag(self, i):
        self.new_tag = None
        k = super().parse_starttag(i)
        if self.new_tag:
            self.new_tag.start_pos = i
            self.new_tag.content_start = k
            self.current_tag = self.new_tag
            if self.new_tag.start_end_tag:
                self.do_close_tag(self.new_tag.tag_name, k, k)
        return k

    def parse_endtag(self, i):
        self.closed_tag_name = None
        k = super().parse_endtag(i)
        if self.closed_tag_name is not None:
            self.do_close_tag(self.closed_tag_name, i, k)
        return k

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.new_tag.start_end_tag = True

    def handle_starttag(self, tag, attrs):
        tag_class = html_tags.tag_types.get(tag, html_tags.Tag)
        self.new_tag = tag_class(self.current_tag, tag, attrs)

    def handle_endtag(self, tag):
        self.closed_tag_name = tag

    def do_close_tag(self, tag_name, i, k):
        found = None
        tag = self.current_tag
        while tag is not None:
            if tag.tag_name == tag_name:
                found = tag
                found.content_end = i
                found.end_pos = k
                break
            tag = tag.parent
        if not found:
            # close tag without opening one
            tag = html_tags.Tag(self.current_tag, tag_name, [])
            tag.start_pos = i
            tag.content_start = i
            tag.content_end = i
            tag.end_pos = k
            return
        while self.current_tag is not None:
            tag = self.current_tag
            self.current_tag = self.current_tag.parent
            if tag == found:
                break
            tag.content_end = i
            tag.end_pos = i

    def convert(self, data: str):
        data = data.replace('\n', '').replace('\t', '')
        self.root = html_tags.Tag(None, '', [])
        self.root.content_start = 0
        self.root.end_pos = len(data)
        self.current_tag = self.root
        self.feed(data)
        self.close()
        return ''.join(self.root.convert(data))

    def close(self):
        super().close()
        while self.current_tag is not None:
            tag = self.current_tag
            self.current_tag = self.current_tag.parent
            tag.content_end = self.root.end_pos
            tag.end_pos = self.root.end_pos


def html_to_bb(text):
    return HtmlConverter().convert(text)
