import pytest


@pytest.mark.django_db
def test_one(client):
    response = client.get('/')
    assert response.status_code == 200
