import pytest
from gistapi.gistapi import app
from unittest.mock import patch


# Mock functions
def mock_gists_for_user(username):
    # Simulate getting gists for a user
    if username == "valid_user":
        return [
            {"id": "1", "files": {"file1.txt": {"filename": "file1.txt"}}},
            {"id": "2", "files": {"file2.txt": {"filename": "file2.txt"}}}
        ]
    elif username == "invalid_user":
        return {
            "message": "Not Found",
            "documentation_url": "https://docs.github.com/rest/gists/gists#list-gists-for-a-user",
            "status": "404"
        }
    else:
        return {"status": "error"}


def mock_get_gist_by_id(gist_id):
    # Simulate getting a gist by its ID
    if (int(gist_id) == 1):
        return {
            "id": 1,
            "files": { "file1.txt": {"content": "example content 9"} }
        }
    else:
        return {
            "id": 2,
            "files": { "file2.txt": {"content": "another example"} }
        }


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@patch('gistapi.gistapi.gists_for_user', side_effect=mock_gists_for_user)
@patch('gistapi.gistapi.get_gist_by_id', side_effect=mock_get_gist_by_id)
def test_search_invalid_user(mock_get_gist_by_id, mock_gists_for_user, client):
    response = client.post('/api/v1/search', json={"username": "invalid_user", "pattern": "example"})
    json_data = response.get_json()
    assert response.status_code == 404
    assert json_data["status"] == "error"
    assert "reason" in json_data
    assert json_data["reason"] == "User's gists not found (incorrent user name?)"


@patch('gistapi.gistapi.gists_for_user', side_effect=mock_gists_for_user)
@patch('gistapi.gistapi.get_gist_by_id', side_effect=mock_get_gist_by_id)
def test_search_invalid_regex(mock_get_gist_by_id, mock_gists_for_user, client):
    response = client.post('/api/v1/search', json={"username": "valid_user", "pattern": "["})
    json_data = response.get_json()
    assert response.status_code == 400
    assert json_data["status"] == "error"
    assert "reason" in json_data
    assert "Error compiling regular expression" in json_data["reason"]


@patch('gistapi.gistapi.gists_for_user', side_effect=mock_gists_for_user)
@patch('gistapi.gistapi.get_gist_by_id', side_effect=mock_get_gist_by_id)
def test_search_success1(mock_get_gist_by_id, mock_gists_for_user, client):
    response = client.post('/api/v1/search', json={"username": "valid_user", "pattern": "example"})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["status"] == "success"
    assert "matches" in json_data
    assert len(json_data["matches"]) == 2


@patch('gistapi.gistapi.gists_for_user', side_effect=mock_gists_for_user)
@patch('gistapi.gistapi.get_gist_by_id', side_effect=mock_get_gist_by_id)
def test_search_success2(mock_get_gist_by_id, mock_gists_for_user, client):
    response = client.post('/api/v1/search', json={"username": "valid_user", "pattern": r"\d"})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["status"] == "success"
    assert json_data["pattern"] == r"\d"
    assert "matches" in json_data
    assert len(json_data["matches"]) == 1


@patch('gistapi.gistapi.gists_for_user', side_effect=mock_gists_for_user)
@patch('gistapi.gistapi.get_gist_by_id', side_effect=mock_get_gist_by_id)
def test_empty_search_success(mock_get_gist_by_id, mock_gists_for_user, client):
    response = client.post('/api/v1/search', json={"username": "valid_user", "pattern": "hello"})
    json_data = response.get_json()
    assert response.status_code == 200
    assert json_data["status"] == "success"
    assert "matches" in json_data
    assert len(json_data["matches"]) == 0
