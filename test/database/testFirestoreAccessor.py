import pytest
import firebase_admin
from firebase_admin import credentials, firestore
from unittest.mock import MagicMock, ANY
from src.database.FirestoreAccessor import FirestoreAccessor


@pytest.fixture()
def mock_app(monkeypatch):
    app_mock = MagicMock()
    init_app_mock = MagicMock(return_value=app_mock)
    monkeypatch.setattr(credentials, "Certificate", lambda x: x)
    monkeypatch.setattr(firebase_admin, "initialize_app", init_app_mock)
    monkeypatch.setattr(firebase_admin, "get_app", lambda: app_mock)
    return init_app_mock

@pytest.fixture
def mock_client(monkeypatch, mock_app):
    client_mock = MagicMock()
    monkeypatch.setattr(firebase_admin.firestore, "client", lambda x: client_mock)
    return client_mock

@pytest.fixture
def mock_ref(mock_client):
    mock_collection = MagicMock()
    mock_client.configure_mock(**{"collection.return_value": mock_collection})
    return mock_collection

def test_init(mock_client, mock_app):
    temp = FirestoreAccessor()
    mock_app.assert_called_with(ANY, {
        'databaseURL': 'https://autodash-9dccb.firebaseio.com/',
        'databaseAuthVariableOverride': {
            'uid': 'pipeline-worker'
        }
    })

def test_fetch_newest_videos(monkeypatch, mock_ref):
    mock_query1 = MagicMock()
    mock_ref.configure_mock(**{"where.return_value":})

    fa = FirestoreAccessor()
    md1 = fa.fetch_newest_videos()
    md2 = fa.fetch_next_metadata()
    assert md1 == 1
    assert md2 == 2
