import json

import pytest
from django import urls

from django_h2.test_client import AsyncClient


@pytest.mark.asyncio
async def test_pm_sse(admin, user):
    admin_client = AsyncClient()
    admin_client.cookies = admin.cookies
    user_client = AsyncClient()
    user_client.cookies = user.cookies
    sse = await user_client.sse('/api/sse/')
    assert sse.status_code == 200
    try:
        response = await admin_client.post(
            urls.reverse('pm:to_user', args=[user.user.pk]),
            {'body': 'hello'},
        )
        assert response.status_code == 302
        assert response.url == urls.reverse('pm:to_user', args=[user.user.pk])
        event = await sse.events.__anext__()
        assert event['event'] == 'pm'
        data = json.loads(event['data'])
        assert data['.action'] == 'new_pm'
    finally:
        sse.close()
