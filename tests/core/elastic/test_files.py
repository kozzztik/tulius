import os
import json
import portalocker
from unittest import mock

import pytest

from tulius.core.elastic import files


@pytest.fixture(name='file_config')
def _test_file_config(tmp_path):
    return {'BASE_DIR': tmp_path}


def test_file_with_no_config(file_config):
    with open(os.path.join(file_config['BASE_DIR'], 'my.log'), 'wb') as f:
        f.write(b'smth\n')

    with files.WorkFile(file_config, 'my') as f:
        data = f.read_bulk(10)
        assert len(data) == 1
        assert data[0].data == b'smth'
        f.data_sent(data[0].end_pos)
    with files.WorkFile(file_config, 'my') as f:
        data = f.read_bulk(10)
        assert data == []


def test_file_with_bad_config(file_config):
    with open(os.path.join(file_config['BASE_DIR'], 'my.log'), 'wb') as f:
        f.write(b'smth\n')
    with open(os.path.join(file_config['BASE_DIR'], 'my.conf'), 'wb') as f:
        f.write(b'smth\n')

    with files.WorkFile(file_config, 'my') as f:
        data = f.read_bulk(10)
        assert len(data) == 1
        assert data[0].data == b'smth'
        f.data_sent(data[0].end_pos)
    with files.WorkFile(file_config, 'my') as f:
        data = f.read_bulk(10)
        assert data == []


def test_json_escaping(file_config):
    with files.WorkFile(file_config, 'my') as f:
        f.write_data({'foo': 'bar\nbar'})
        f.write_data({'bar': 'foo\nfoo'})
    with files.WorkFile(file_config, 'my') as f:
        data = f.read_bulk(10)
        assert len(data) == 2
        assert data[0].data['foo'] == 'bar\nbar'
        assert data[1].data['bar'] == 'foo\nfoo'


def test_binary_escaping(file_config):
    with files.WorkFile(file_config, 'my') as f:
        f.write_data(b'foo\nbar')
        f.write_data(b'bar\nfoo')
    with files.WorkFile(file_config, 'my') as f:
        data = f.read_bulk(10)
        assert len(data) == 2
        assert data[0].data == b'foo\\nbar'
        assert isinstance(data[0].exc, json.JSONDecodeError)
        assert data[1].data == b'bar\\nfoo'
        assert isinstance(data[1].exc, json.JSONDecodeError)


def test_cache_limit(file_config):
    file_config['CACHE_LIMIT'] = 2
    with files.WorkFile(file_config, 'my') as f:
        f.write_data(b'1')
        f.write_data(b'2')
        f.write_data(b'3')
        f.write_data(b'4')
        assert len(f.cache) == 2
        assert f.cache[0].data == b'1'
        assert f.cache[1].data == b'2'


def test_cache_limit_and_read(file_config):
    file_config['CACHE_LIMIT'] = 2
    with files.WorkFile(file_config, 'my') as f:
        f.write_data(1)
        f.write_data(2)
        f.write_data(3)
        assert len(f.cache) == 2
        data = f.read_bulk(1)
        assert len(data) == 1
        assert data[0].data == 1
        f.data_sent(data[0].end_pos)
        assert len(f.cache) == 1
        f.write_data(4)
        assert len(f.cache) == 1
        data = f.read_bulk(10)
        assert len(data) == 3
        assert data[0].data == 2
        assert data[1].data == 3
        assert data[2].data == 4


def test_opening_locked_file(file_config):
    with open(os.path.join(file_config['BASE_DIR'], 'my.log'), 'wb') as f:
        f.write(b'smth\n')
        portalocker.lock(f, portalocker.LockFlags.EXCLUSIVE)
        try:
            with pytest.raises(OSError):
                files.WorkFile(file_config, 'my')
        finally:
            portalocker.unlock(f)


def test_close_with_fail_lock_file(file_config):
    with mock.patch.object(files, 'portalocker') as locker_mock:
        locker_mock.unlock.side_effect = OSError
        with files.WorkFile(file_config, 'my'):
            pass
    assert locker_mock.unlock.called


def test_concurrent_file_remove(file_config):
    def close():
        files.WorkFile.close(f)
        # after close other process removes files
        os.remove(f._data_fd_name)
        os.remove(f._config_fd_name)
    f = files.WorkFile(file_config, 'my')
    with mock.patch.object(f, 'close', side_effect=close) as close_mock:
        f.remove()
    assert close_mock.called


def test_concurrent_file_remove_opened(file_config):
    f2 = None

    def close():
        files.WorkFile.close(f)
        # after close other process open files
        nonlocal f2
        f2 = files.WorkFile(file_config, 'my')
    f = files.WorkFile(file_config, 'my')
    with mock.patch.object(f, 'close', side_effect=close):
        f.remove()
    assert f2
    f2.close()
