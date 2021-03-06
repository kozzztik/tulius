import os

import pytest
import django
from django.test import client as django_client
from django.test import utils


class JSONClient(django_client.Client):
    # pylint: disable=too-many-arguments
    def post(
            self, path, data=None,
            content_type=django_client.MULTIPART_CONTENT,
            follow=False, secure=False, **extra):
        if isinstance(data, dict):
            content_type = 'application/json'
        return super().post(
            path, data, content_type=content_type, follow=follow,
            secure=secure, **extra)

    # pylint: disable=too-many-arguments
    def put(self, path, data='', content_type='application/octet-stream',
            follow=False, secure=False, **extra):
        if isinstance(data, dict):
            content_type = 'application/json'
        return super().put(
            path, data=data, content_type=content_type, follow=follow,
            secure=secure, **extra)

    # pylint: disable=too-many-arguments
    def options(self, path, data='', content_type='application/octet-stream',
                follow=False, secure=False, **extra):
        if isinstance(data, dict):
            content_type = 'application/json'
        return super().options(
            path, data=data, content_type=content_type, follow=follow,
            secure=secure, **extra)


@pytest.fixture(name='client')
def client_fixture():
    return JSONClient()


@pytest.fixture(name='user_factory', scope='session')
def create_user_fixture():
    user_number = 0

    def user_factory(username=None, **kwargs):
        # pylint: disable=C0415
        from tulius import models as tulius_models

        username = username or f'user_{user_number}'
        user = tulius_models.User(
            username=username, email=f'{username}@tulius.com', **kwargs)
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


def init_settings():
    os.environ["TULIUS_TEST"] = "1"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'settings')
    django.setup()
    utils.setup_test_environment()


init_settings()


@pytest.mark.trylast
def pytest_sessionstart(session):
    session.django_db_cfg = utils.setup_databases(
        verbosity=session.config.option.verbose,
        interactive=False,
        keepdb=False
    )


@pytest.mark.trylast
def pytest_sessionfinish(session, exitstatus):
    db_cfg = getattr(session, 'django_db_cfg')
    if db_cfg:
        utils.teardown_databases(
            db_cfg, verbosity=session.config.option.verbose)
