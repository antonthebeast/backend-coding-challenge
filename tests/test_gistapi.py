import pytest
from gistapi.gistapi import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_ping(client):
    response = client.get('/ping')
    assert response.status_code == 200
    assert response.data == b'pong'


def test_search_missing_username(client):
    response = client.post('/api/v1/search', json={"pattern": "example"})
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data["status"] == "error"
    assert "reason" in json_data
    assert json_data["reason"] == "Missing 'username' key in JSON data"


def test_search_missing_pattern(client):
    response = client.post('/api/v1/search', json={"username": "valid_user"})
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data["status"] == "error"
    assert "reason" in json_data
    assert json_data["reason"] == "Missing 'pattern' key in JSON data"


def test_search_invalid_request(client):
    response = client.post('/api/v1/search', data="hello")
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data["status"] == "error"
    assert "reason" in json_data
    assert "Bad Request" in json_data["reason"]


