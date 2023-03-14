import asyncio

import json

import pytest

from tulius.forum.threads import models
from tulius.websockets.asgi.utils import AsyncClient


@pytest.mark.asyncio
async def test_comments_ws(thread, superuser, admin, user):
    wss = {}
    clients = {}
    try:
        for u in [superuser, admin, user]:
            clients[u] = client = AsyncClient()
            client.cookies = u.cookies
            wss[u] = await client.ws('/api/ws/')
            response = await client.get(thread['url'])
            assert response.status_code == 200
        await wss[user].send_text(json.dumps({
            'action': 'subscribe_comments', 'id': thread['id']}))
        # post comment to thread
        response = await clients[admin].post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'ho ho ho', 'body': 'happy new year',
                'media': {},
            })
        assert response.status_code == 200
        data = await wss[user].receive_text()
        data = json.loads(data)
        assert data['.namespaced'] == 'thread_comments'
        assert data['.action'] == 'new_comment'
        assert data['parent_id'] == thread['id']
        assert wss[admin].send_queue == []
        assert wss[superuser].send_queue == []
        # again, but unsubscribe
        await wss[user].send_text(json.dumps({
            'action': 'unsubscribe_comments', 'id': thread['id']}))
        await wss[superuser].send_text(json.dumps({
            'action': 'subscribe_comments', 'id': thread['id']}))
        response = await clients[admin].post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'ho ho ho', 'body': 'happy new year2',
                'media': {},
            })
        assert response.status_code == 200
        data = await wss[superuser].receive_text()
        data = json.loads(data)
        assert data['.namespaced'] == 'thread_comments'
        assert data['.action'] == 'new_comment'
        assert data['parent_id'] == thread['id']
        assert wss[user].send_queue == []
        assert wss[admin].send_queue == []
    finally:
        for u in wss.values():
            u.close()


@pytest.mark.asyncio
async def test_comments_ws_no_rights(room_group, superuser, admin, user):
    client = AsyncClient()
    client.cookies = admin.cookies
    response = await client.put(
        room_group['url'], {
            'title': 'thread', 'body': 'thread description',
            'room': False, 'default_rights': models.NO_ACCESS,
            'granted_rights': [], 'important': False, 'media': {}})
    assert response.status_code == 200
    thread = response.json()
    wss = {}
    clients = {}
    try:
        for u in [superuser, admin, user]:
            clients[u] = client = AsyncClient()
            client.cookies = u.cookies
            wss[u] = await client.ws('/api/ws/')
            response = await client.get(thread['url'])
            if u is user:
                assert response.status_code == 403
            else:
                assert response.status_code == 200
            await wss[u].send_text(json.dumps({
                'action': 'subscribe_comments', 'id': thread['id']}))
        # post comment to thread
        response = await clients[admin].post(
            thread['url'] + 'comments_page/', {
                'reply_id': thread['first_comment_id'],
                'title': 'ho ho ho', 'body': 'happy new year',
                'media': {},
            })
        assert response.status_code == 200
        for u in [superuser, admin]:
            data = await wss[u].receive_text()
            data = json.loads(data)
            assert data['.namespaced'] == 'thread_comments'
            assert data['.action'] == 'new_comment'
            assert data['parent_id'] == thread['id']
        assert wss[user].send_queue == []
    finally:
        for u in wss.values():
            u.close()
