from django import dispatch
from django.conf import settings

from redis import client

from tulius.forum.threads import signals
from tulius.forum import online_status


@dispatch.receiver(signals.after_create)
def cleanup_caches(instance, **_kwargs):
    redis = client.Redis(**settings.REDIS_CONNECTION)
    redis.delete(online_status.thread_key(instance.__class__, instance.pk))


def test_online_status(thread, admin, user):
    # check online on thread
    response = admin.get(f'/api/forum/online_status/{thread["id"]}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == admin.user.pk
    # check online by other user
    response = user.get(f'/api/forum/online_status/{thread["id"]}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 2
    assert data['users'][0]['id'] == admin.user.pk
    assert data['users'][1]['id'] == user.user.pk
    # check online on root
    response = admin.get(f'/api/forum/online_status/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) >= 2
    ids = [u['id'] for u in data['users']]
    assert admin.user.pk in ids
    assert user.user.pk in ids


def test_hiding_status(thread, admin):
    admin.user.show_online_status = True
    admin.user.save()
    # visit thread to became online
    response = admin.get(f'/api/forum/online_status/{thread["id"]}/')
    assert response.status_code == 200
    data = response.json()
    assert len(data['users']) == 1
    assert data['users'][0]['id'] == admin.user.pk
    # check status on comments
    response = admin.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert data['comments'][0]['user']['online_status'] is True
    # hide online status
    admin.user.show_online_status = False
    admin.user.save()
    # check status on comments
    response = admin.get(thread['url'] + 'comments_page/')
    assert response.status_code == 200
    data = response.json()
    assert data['comments'][0]['user']['online_status'] is False
