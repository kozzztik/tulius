import os

import pytest
import django
from django.test import client as django_client


class JSONClient(django_client.Client):
    # pylint: disable=too-many-arguments
    def post(
            self, path, data=None, content_type=django_client.MULTIPART_CONTENT,
            follow=False, secure=False, **extra):
        if isinstance(data, dict):
            content_type = 'application/json'
        return super(JSONClient, self).post(
            path, data, content_type=content_type, follow=follow, secure=secure,
            **extra)

    # pylint: disable=too-many-arguments
    def put(self, path, data='', content_type='application/octet-stream',
            follow=False, secure=False, **extra):
        if isinstance(data, dict):
            content_type = 'application/json'
        return super(JSONClient, self).put(
            path, data=data, content_type=content_type, follow=follow,
            secure=secure, **extra)

    # pylint: disable=too-many-arguments
    def options(self, path, data='', content_type='application/octet-stream',
                follow=False, secure=False, **extra):
        if isinstance(data, dict):
            content_type = 'application/json'
        return super(JSONClient, self).options(
            path, data=data, content_type=content_type, follow=follow,
            secure=secure, **extra)


@pytest.fixture(name='client')
def client_fixture():
    return JSONClient()


@pytest.fixture(name='user_factory', scope='session')
def create_user_fixture():
    user_number = 0

    def user_factory(username=None, **kwargs):
        from tulius import models as tulius_models

        username = username or f'user_{user_number}'
        user = tulius_models.User(username=username, **kwargs)
        user.set_password(username)
        user.save()
        client = JSONClient()
        client.user = user
        client.login(username=username, password=username)
        return client
    return user_factory


@pytest.fixture(name='superuser', scope='session')
def superuser_fixture(user_factory):
    return user_factory(is_superuser=True, username='kozzztik')


@pytest.fixture(name='admin', scope='session')
def admin_fixture(user_factory):
    return user_factory(username='Tulius')


@pytest.fixture(name='user', scope='session')
def user_fixture(user_factory):
    return user_factory(username='John Doe')


@pytest.mark.trylast
def pytest_configure():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'settings')
    from django.conf import settings

    if not settings.configured:
        django.setup()
    from django.test import utils
    utils.setup_test_environment()


@pytest.mark.trylast
def pytest_sessionstart(session):
    from django.test import utils
    session.django_db_cfg = utils.setup_databases(
        verbosity=session.config.option.verbose,
        interactive=False,
        keepdb=False
    )


@pytest.mark.trylast
def pytest_sessionfinish(session, exitstatus):
    db_cfg = getattr(session, 'django_db_cfg')
    if db_cfg:
        from django.test import utils
        utils.teardown_databases(db_cfg, verbosity=session.config.option.verbose)
