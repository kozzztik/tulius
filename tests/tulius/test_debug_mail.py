from unittest import mock

import pytest
from django.core import mail
from django.conf import settings

from tulius.core.debug_mail import backend


def test_debug_mail(tmp_path, superuser, admin):
    d = tmp_path / "mail"
    d.mkdir()
    settings.EMAIL_FILE_PATH = str(d)
    email_backend = backend.EmailBackend()
    result = email_backend.send_messages([
        mail.EmailMessage(
            'subject', 'body', 'sender@tulius.com',
            ['foo@bar.com', 'bar@bar.com'])])
    assert result == 2
    # check recipients list
    response = admin.get('/api/debug_mail/')
    assert response.status_code == 403
    response = superuser.get('/api/debug_mail/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['result']) == 2
    # query
    response = superuser.get('/api/debug_mail/?q=foo')
    assert response.status_code == 200
    data = response.json()
    assert len(data['result']) == 1
    assert data['result'][0]['name'] == 'foo@bar.com'
    # get mail box
    response = admin.get('/api/debug_mail/foo@bar.com/')
    assert response.status_code == 403
    response = superuser.get('/api/debug_mail/foo@bar.com/')
    assert response.status_code == 200
    data = response.json()
    name = data['result'][0]['name']
    # get mail data
    response = admin.get(f'/api/debug_mail/foo@bar.com/{name}/')
    assert response.status_code == 403
    response = superuser.get(f'/api/debug_mail/foo@bar.com/{name}/')
    assert response.status_code == 200
    data = response.content.decode()
    assert 'subject' in data
    assert 'body' in data


def test_debug_mail_fail_silently():
    write = mock.MagicMock(side_effect=Exception('foo'))
    email_backend = backend.EmailBackend(fail_silently=True)
    email_backend.write_message = write
    result = email_backend.send_messages([
        mail.EmailMessage(
            'subject', 'body', 'sender@tulius.com',
            ['foo@bar.com', 'bar@bar.com'])])
    assert result == 0
    assert write.called
    email_backend = backend.EmailBackend(fail_silently=False)
    email_backend.write_message = write
    with pytest.raises(Exception) as exc:
        email_backend.send_messages([
            mail.EmailMessage(
                'subject', 'body', 'sender@tulius.com',
                ['foo@bar.com', 'bar@bar.com'])])
    assert exc.value.args[0] == 'foo'
    assert write.call_count == 2
