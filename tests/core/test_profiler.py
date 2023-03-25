import logging
from unittest import mock

from ua_parser import user_agent_parser
from tulius.core.elastic import indexing


def test_profiler_minor_versions(client):
    parser = mock.MagicMock(return_value={
        'user_agent': {
            'family': 'Netscape',
            'major': '5',
            'minor': '0',
        },
        'os': {
            'family': 'WindowsNT 4',
            'major': '',
            'minor': '0',
        },
        'device': {
            'family': 'iPhone',
        }
    })
    index = mock.MagicMock()
    with mock.patch.object(user_agent_parser, 'Parse', parser):
        with mock.patch.object(indexing._indexer, 'index', index):
            response = client.get('/')
    assert response.status_code == 200
    assert index.called
    assert index.call_args[0][0]['browser_version'] == '5.0'
    assert index.call_args[0][0]['os_version'] == '4.0'


def test_profiler_parse_exception(client):
    logger = logging.getLogger('django.request')
    error = mock.MagicMock()
    with mock.patch.object(
            user_agent_parser, 'Parse', side_effect=Exception('foo')):
        with mock.patch.object(logger, 'error', error):
            response = client.get('/')
    assert response.status_code == 200
    assert error.called
