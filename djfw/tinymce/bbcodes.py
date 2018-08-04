import logging

from django.utils.translation import ugettext_lazy as _


bb_codes_list = {}
bb_simple_codes_list = {'br': '<br/>'}


def bbcode_to_html(data_str, codes_list=None, simple_codes_list=None):
    current = 0
    state = 0
    tag_stack = []
    if simple_codes_list is None:
        simple_codes_list = bb_simple_codes_list
    if codes_list is None:
        codes_list = bb_codes_list
    while current < len(data_str):
        if data_str[current] == '[':
            tag_opened = current
            if (len(data_str) > current + 1) and (
                    data_str[current + 1] == '/'):
                state = 2
                tagname_start = current + 2
            else:
                state = 1
                tagname_start = current + 1
        elif (data_str[current] == ']') and (state != 0):
            tagname = data_str[tagname_start:current].strip()
            if tagname:
                if state == 1:
                    param = None
                    tagname_list = tagname.split('=', 1)
                    tagname = tagname_list[0].strip().lower()
                    if len(tagname_list) > 1:
                        param = tagname_list[1].strip().replace('"', '')
                    if tagname:
                        if tagname in simple_codes_list:
                            tag = simple_codes_list[tagname]
                            data = None
                            if callable(tag):
                                try:
                                    data = tag(tagname, param)
                                except:
                                    pass
                            else:
                                data = tag
                            if data is not None:
                                old_len = current - tag_opened
                                data_str = data_str[0:tag_opened] + data + \
                                    data_str[(current + 1):len(data_str)]
                                current = current + len(data) - old_len - 1
                        elif tagname in codes_list:
                            tag = codes_list[tagname]
                            tag_stack.append(
                                (tag, tagname, param, tag_opened, current + 1))
                elif state == 2:
                    tagname = tagname.lower()
                    new_tag_stack = tag_stack[:]
                    tag = None
                    while new_tag_stack:
                        (stack_tag, stack_tagname, stack_param,
                         stack_tag_opened, stack_current) = \
                            new_tag_stack.pop()
                        if stack_tagname == tagname:
                            tag = stack_tag
                            tag_stack = new_tag_stack
                            break
                    if tag:
                        data = None
                        text = data_str[stack_current:tag_opened]
                        try:
                            data = tag(stack_tagname, stack_param, text)
                        except:
                            pass
                        if data is not None:
                            old_len = current - stack_tag_opened
                            data_str = data_str[0:stack_tag_opened] + data + \
                                data_str[(current + 1):len(data_str)]
                            current = current + len(data) - old_len - 1
                state = 0
        current += 1
    return data_str


def register_bb_code(name):
    def wrapper(f):
        bb_codes_list[name] = f
        return f
    return wrapper


def bb_simple_nested(tagname, param, text):
    return '<%s>%s</%s>' % (tagname, text, tagname)


bb_codes_list['i'] = bb_simple_nested
bb_codes_list['b'] = bb_simple_nested
bb_codes_list['u'] = bb_simple_nested
bb_codes_list['s'] = bb_simple_nested
bb_codes_list['big'] = bb_simple_nested
bb_codes_list['small'] = bb_simple_nested

VALID_BB_COLORS = [
    'darkred', 'red', 'orange', 'brown', 'yellow', 'green', 'olive', 'cyan',
    'blue', 'darkblue', 'indigo', 'violet', 'white', 'black']


@register_bb_code('color')
def bb_color(tagname, param, text):
    param = param.lower().strip()
    param_checked = False
    if param in VALID_BB_COLORS:
        param_checked = True
    if (not param_checked) and (len(param) == 7):
        param_checked = True
        for c in param[1:7]:
            if c not in 'abcdef0123456789':
                param_checked = False
                break
    if not param_checked:
        raise Exception('Invalid color')
    return '<span style="color: %s;">%s</span>' % (param, text)


@register_bb_code('url')
def bb_url(tagname, param, text):
    if param:
        param = param.replace('"', '&quot;').replace('\n', '')
        return '<a href="%s">%s</a>' % (param, text)
    text = text.replace('"', '&quot;').replace('\n', '')
    return '<a href="%s">%s</a>' % (text, text)


@register_bb_code('img')
def bb_img(tagname, param, text):
    text = text.replace('"', '&quot;').replace('\n', '')
    if param:
        param = param.replace('"', '&quot;').replace('\n', '')
        return '<img src="%s" alt="%s" />' % (param, text)
    return '<img src="%s"/>' % (text)


@register_bb_code('quote')
def bb_quote(tagname, param, text):
    if param:
        param += ' ' + str(_('said'))
        return '<blockquote><small>%s</small>%s</blockquote>' % (param, text,)
    return '<blockquote>%s</blockquote>' % (text,)


@register_bb_code('center')
def bb_center(tagname, param, text):
    return '<div align="center">%s</div>' % (text,)


@register_bb_code('code')
def bb_code(tagname, param, text):
    return '<tt>%s</tt>' % (text,)


VALID_BB_FONT_SIZES = [
    'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']


@register_bb_code('size')
def bb_size(tagname, param, text):
    param = param.strip()
    if param not in VALID_BB_FONT_SIZES:
        param = param.replace('px', '').strip()
        param = int(param)
        param = str(param) + 'px'
    return '<span style="font-size:%s;">%s</span>' % (param, text)


def bb_datablock(tagname, param):
    try:
        from djfw.datablocks.models import DataBlock
        block = DataBlock.objects.languaged().filter(name=param)[0]
        return block.full_text
    except Exception as e:
        logging.error(e)
        return ''


bb_simple_codes_list['datablock'] = bb_datablock
