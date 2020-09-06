import datetime
from unittest import mock

import pytest
from django.core import management


@pytest.fixture(name='inspect')
def inspect_fixture():
    inspect = mock.MagicMock()
    inspect.stats.return_value = []
    inspect.active.return_value = {'worker': [
        {'time_start': 1599422960, 'name': 'task1'}]}
    with mock.patch('tulius.celery.app.control.inspect', return_value=inspect):
        yield inspect


def test_celery_status(superuser, admin, inspect):
    # check permissions
    response = admin.get('/api/celery_status/')
    assert response.status_code == 403
    # smoke test
    response = superuser.get('/api/celery_status/')
    assert response.status_code == 200
    data = response.json()
    assert 'stats' in data
    assert data['active']['worker'][0]['time_start'] == '2020-09-06 23:09:20'


def test_wait_celery_smoke(celery_worker, inspect):
    inspect.active.return_value['worker'] = []
    management.execute_from_command_line(['manage.py', 'wait_celery'])


def test_wait_celery_waits_tasks(inspect):
    time_mock = mock.MagicMock()
    time_mock.sleep.side_effect = Exception('bar')
    with mock.patch('tulius.management.commands.wait_celery.time', time_mock):
        with pytest.raises(Exception) as e:
            management.execute_from_command_line(['manage.py', 'wait_celery'])
        assert e.value.args[0] == 'bar'
    assert time_mock.sleep.called
    assert inspect.active.called
