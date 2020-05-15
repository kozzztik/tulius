from djfw.wysibb.templatetags import bb_parser


def test_lists():
    result = bb_parser.bbcode_to_html('[list=1]\n[*]gdrgdrg\n[*] \n[/list]\n')
    assert result == '<ol><li>gdrgdrg</li><li></li></ol><br/>'
    result = bb_parser.bbcode_to_html(
        '[list=1]\n[*]gdrgdrg[/*][*] [/*]\n[/list]\n')
    assert result == '<ol><br/><li>gdrgdrg</li><li> </li><br/></ol><br/>'
