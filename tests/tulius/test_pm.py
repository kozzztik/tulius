import pytest

from django import urls

from tulius.websockets.asgi.utils import AsyncClient
from django.test import client as django_client


@pytest.mark.asyncio
async def test_comments_ws(superuser, admin, user):
    wss = {}
    clients = {}
    try:
        for u in [superuser, admin, user]:
            clients[u] = client = AsyncClient()
            client.cookies = u.cookies
            wss[u] = await client.ws('/api/ws/old/')
        # check is ready
        await wss[user].send_text("ping")
        data = await wss[user].receive_text(timeout=10)
        assert data == 'ping/answer'
        # post comment to thread
        response = await clients[admin].post(
            urls.reverse('pm:to_user', args=[user.user.pk]),
            {'body': 'hello'},
            content_type=django_client.MULTIPART_CONTENT
        )
        assert response.status_code == 302
        assert response.url == urls.reverse('pm:to_user', args=[user.user.pk])
        data = await wss[user].receive_text(timeout=30)
        assert data.startswith('new_pm ')
        assert wss[superuser].send_queue == []
        assert wss[admin].send_queue == []
    finally:
        for u in wss.values():
            u.close()
