import os
import pytest
import django


@pytest.fixture(name='client')
def client_fixture():
    from django.test.client import Client
    return Client()


@pytest.fixture(name='user_factory', scope='session')
def create_user_fixture():
    user_number = 0

    def user_factory(username=None, **kwargs):
        from tulius import models as tulius_models
        from django import test

        username = username or f'user_{user_number}'
        user = tulius_models.User(username=username, **kwargs)
        user.set_password(username)
        user.save()
        client = test.Client()
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
