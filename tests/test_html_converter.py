from unittest import mock

import pytest

from tulius.core.ckeditor import html_converter
from djfw.wysibb import models
from djfw.wysibb.templatetags import bbcodes


@pytest.mark.parametrize('data,value', [
    [   # Check structure support
        'aaa<b>d<some_tag>f</some_tag>f<s>fd</s>ff</b>bb',
        'aaa[b]dff[s]fd[/s]ff[/b]bb'
    ],
    [   # Test self closing tags and BR tag convert
        '<br/><b>df<sometag/>d<br/>f<br/>brb<br/></b>',
        '\n[b]dfd\nf\nbrb\n[/b]'
    ],
    [  # Closing tag typo
        '<br/><b>df<sometag/>d<br/>f<br/>brb<br/><b/>',
        '\n[b]dfd\nf\nbrb\n[b][/b][/b]'
    ],
    [  # Missing closing tag
        '1<b>22<s>333</b>',
        '1[b]22[s]333[/s][/b]'
    ],
    [  # Close tag without opening one
        '1<b>22</s>3</br>33</sometag>4</b></u>',
        '1[b]223334[/b]'
    ],
])
def test_html_convertor(data, value):
    assert html_converter.html_to_bb(data) == value


@pytest.mark.parametrize('data,value', [
    [   # check ul list
        '11<ul>2<li>33</li><li></li><li>5</li></ul>',
        '11[list]2[*]33\n[*]\n[*]5\n[/list]'
    ],
    [  # check ol list
        '11<ol>2<li>33</li><li></li><li>5</li></ol>',
        '11[list=1]2[*]33\n[*]\n[*]5\n[/list]'
    ],

])
def test_lists(data, value):
    assert html_converter.HtmlConverter().convert(data) == value


@pytest.mark.parametrize('data,value', [
    [   # check invalid colors
        '11<font color="someth">23</font>', '1123'
    ],
    [  # check valid number color
        '11<font color="#ff00ff">23</font>', '11[color=#ff00ff]23[/color]'
    ],
    [  # check valid text color
        '11<font color="red">23</font>', '11[color=red]23[/color]'
    ],
    [  # check empty color
        '11<font>23</font>', '1123'
    ],
])
def test_font(data, value):
    assert html_converter.HtmlConverter().convert(data) == value


@pytest.mark.parametrize('data,value', [
    [   # check empty span
        '11<span>23</span>', '1123'
    ],
    [  # check invalid color
        '11<span style="color: smth">23</span>', '1123'
    ],
    [  # check invalid size
        '11<span style="font-size: 100">23</span>', '1123'
    ],
    [  # check color
        '11<span style="color: #ff00ff">23</span>',
        '11[color=#ff00ff]23[/color]'
    ],
    [  # check size
        '11<span style="font-size: 150%">23</span>',
        '11[size=150]23[/size]'
    ],
    [  # check together color and size
        '11<span style="color: #ff00ff; font-size: 150%">23</span>',
        '11[color=#ff00ff][size=150]23[/size][/color]'
    ],
])
def test_span(data, value):
    assert html_converter.HtmlConverter().convert(data) == value


@pytest.mark.parametrize('data,value', [
    [   # check invalid a tag
        '11<a>23</a>', '1123'
    ],
    [  # check valid tag
        '11<a href="tulius.com">23</a>', '11[url=tulius.com]23[/url]'
    ],
    [  # check removing bad chars
        '11<a href="tulius.com]bad">23</a>', '11[url=tulius.combad]23[/url]'
    ],
])
def test_a_tag(data, value):
    assert html_converter.HtmlConverter().convert(data) == value


@pytest.mark.parametrize('data,value', [
    [   # check invalid a tag
        '11<img>23</img>', '11'
    ],
    [  # check valid tag
        '11<img src="tulius.com" alt="23"/>', '11[img=tulius.com]23[/img]'
    ],
    [  # check removing bad chars
        '11<img src="tulius.com]bad"/>', '11[img=tulius.combad][/img]'
    ],
])
def test_img_tag(data, value):
    with mock.patch.object(bbcodes.smiles, 'smile_dict', return_value={}):
        assert html_converter.HtmlConverter().convert(data) == value


@pytest.fixture(name='smiles')
def smiles_fixture():
    obj = models.Smile(name='angel', text=':angel:')
    obj.image.name = 'wysibb/smiles/angel.gif'
    smiles = {':angel:': '/media/wysibb/smiles/angel.gif'}
    with mock.patch.object(bbcodes.smiles, 'smile_dict', return_value=smiles):
        with mock.patch.object(bbcodes.smiles, 'get_list', return_value=[obj]):
            yield


def test_smiles(smiles):
    original = '<p><img alt=":angel:" src="/media/wysibb/smiles/angel.gif"'\
        ' style="height:26px; width:27px" title=":angel:" /></p>'
    converted = html_converter.html_to_bb(original)
    result = bbcodes.bbcode(converted)
    assert result == '<img class="sm" src="/media/wysibb/smiles/angel.gif"' \
                     ' title="angel" /><br/>'


def test_special_symbols(smiles):
    original = '&Iuml;'
    converted = html_converter.html_to_bb(original)
    assert bbcodes.bbcode(converted) == original


def test_paragraph_line_breaks():
    original = '<p>1</p>\n\n<p>2</p>\n\n<p>3</p>\n'
    assert html_converter.html_to_bb(original) == '1\n2\n3\n'
