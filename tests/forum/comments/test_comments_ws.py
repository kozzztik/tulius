import json

import pytest
from django_h2.test_client import AsyncClient
from tulius.forum.threads import models


@pytest.mark.asyncio
async def test_comments_sse(thread, user, admin):
    user_client = AsyncClient()
    admin_client = AsyncClient()
    user_client.cookies = user.cookies
    admin_client.cookies = admin.cookies
    sse = await user_client.sse(thread['url'] + 'comments_sse/')
    assert sse.status_code == 200
    try:
        response = await user_client.get(thread['url'])
        assert response.status_code == 200
        # post comment to thread
        response = await admin_client.post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'ho ho ho', 'body': 'happy new year',
                'media': {},
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        event = await sse.events.__anext__()
        assert event['event'] == 'thread_comments'
        data = json.loads(event['data'])
        assert data['.action'] == 'new_comment'
        assert data['parent_id'] == thread['id']
    finally:
        sse.close()


@pytest.mark.asyncio
async def test_comments_sse_no_rights(room_group, superuser, admin, user):
    admin_client = AsyncClient()
    admin_client.cookies = admin.cookies
    response = await admin_client.put(
        room_group['url'],
        {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'important': False, 'media': {}
        },
        content_type='application/json'
    )
    assert response.status_code == 200
    thread = response.json()
    user_client = AsyncClient()
    user_client.cookies = user.cookies
    response = await user_client.sse(thread['url'] + 'comments_sse/')
    assert response.status_code == 403
    superuser_client = AsyncClient()
    superuser_client.cookies = superuser.cookies
    sse = await superuser_client.sse(thread['url'] + 'comments_sse/')
    assert sse.status_code == 200
    try:
        response = await admin_client.post(
            thread['url'] + 'comments_page/',
            {
                'reply_id': thread['first_comment_id'],
                'title': 'ho ho ho', 'body': 'happy new year',
                'media': {},
            },
            content_type='application/json'
        )
        assert response.status_code == 200
        event = await sse.events.__anext__()
        assert event['event'] == 'thread_comments'
        data = json.loads(event['data'])
        assert data['.action'] == 'new_comment'
        assert data['parent_id'] == thread['id']
    finally:
        sse.close()
