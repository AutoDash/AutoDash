import pytest
import firebase_admin
from firebase_admin import credentials, firestore
from unittest.mock import MagicMock, ANY
from src.database.FirestoreAccessor import FirestoreAccessor, QueryFilter
from src.database.iDatabase import NotExistingException
from ..test_hepler import sample_mdi_dict, sample_mdi
from src.data.MetaDataItem import MetaDataItem


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

def test_fetch_newest_videos_simple(monkeypatch, mock_ref):
    mdi_dict = sample_mdi_dict()

    mock_query = MagicMock()
    mock_md = MagicMock(id=mdi_dict["id"])

    mock_query.configure_mock(**{
        "order_by.return_value": mock_query,
        "stream.return_value": iter([mock_md]),
        "where.return_value": mock_query,
    })
    mock_ref.configure_mock(**{
        "where.return_value": mock_query,
    })
    mock_md.configure_mock(**{
        "to_dict.return_value": mdi_dict,
    })

    fa = FirestoreAccessor()
    it = fa.fetch_newest_videos(last_timestamp=10)
    md = next(it)

    mock_ref.where.assert_called_once_with("date_created", ">", 10)
    mock_query.order_by.assert_called_once_with("date_created", direction=firestore.Query.DESCENDING)
    mock_md.to_dict.assert_called_once_with()
    assert md.id == mdi_dict["id"]

def test_fetch_newest_videos_processed_query(monkeypatch, mock_ref):
    mdi_dict = sample_mdi_dict()
    mock_query = MagicMock()
    mock_md = MagicMock(id=mdi_dict["id"])

    mock_query.configure_mock(**{
        "order_by.return_value": mock_query,
        "stream.return_value": iter([mock_md]),
        "where.return_value": mock_query,
    })
    mock_ref.configure_mock(**{
        "where.return_value": mock_query,
    })
    mock_md.configure_mock(**{
        "to_dict.return_value": mdi_dict,
    })

    fa = FirestoreAccessor(filter=QueryFilter.PROCESSED)
    it = fa.fetch_newest_videos(last_timestamp=10)
    md = next(it)

    mock_ref.where.assert_called_once_with("date_created", ">", 10)
    mock_query.order_by.assert_called_once_with("date_created", direction=firestore.Query.DESCENDING)
    mock_query.where.assert_called_once_with("tags.state", "==", "processed")
    mock_md.to_dict.assert_called_once_with()
    assert md.id == mdi_dict["id"]

def test_fetch_newest_videos_labelled_query(monkeypatch, mock_ref):
    mdi_dict = sample_mdi_dict()
    mock_query = MagicMock()
    mock_md = MagicMock(id=mdi_dict["id"])

    mock_query.configure_mock(**{
        "order_by.return_value": mock_query,
        "stream.return_value": iter([mock_md]),
        "where.return_value": mock_query,
    })
    mock_ref.configure_mock(**{
        "where.return_value": mock_query,
    })
    mock_md.configure_mock(**{
        "to_dict.return_value": mdi_dict,
    })

    fa = FirestoreAccessor(filter=QueryFilter.LABELLED)
    it = fa.fetch_newest_videos(last_timestamp=10)
    md = next(it)

    mock_ref.where.assert_called_once_with("date_created", ">", 10)
    mock_query.order_by.assert_called_once_with("date_created", direction=firestore.Query.DESCENDING)
    mock_query.where.assert_any_call("tags.state", "==", "processed")
    mock_query.where.assert_any_call("is_cancelled", "==", False)
    mock_md.to_dict.assert_called_once_with()
    assert md.id == mdi_dict["id"]

def test_publish_new_metadata(mock_ref):
    mdi = sample_mdi()

    mock_doc = MagicMock(id=20)
    mock_query = MagicMock()
    mock_ref.configure_mock(**{
        "add.return_value": mock_doc,
        "where.return_value": mock_query,
    })
    mock_query.configure_mock(**{
        "limit.return_value": mock_query,
        "get.return_value": [],
    })

    fa = FirestoreAccessor()
    new_id = fa.publish_new_metadata(mdi)
    assert new_id == 20
    mock_ref.add.assert_called_once_with(sample_mdi_dict())

def test_metadata_exists(mock_ref):
    mock_doc = MagicMock()
    mock_doc.configure_mock(**{
        "get.return_value": MagicMock(exists=True),
    })
    mock_ref.configure_mock(**{
        "document.return_value": mock_doc,
    })
    mdi_id = "100"

    fa = FirestoreAccessor()
    res = fa.metadata_exists(mdi_id)
    mock_ref.document.assert_called_once_with(mdi_id)
    mock_doc.get.assert_called_once_with()

    assert res == True

def test_url_exists_does_exist(mock_ref):
    mock_query = MagicMock()
    mock_query.configure_mock(**{
        "limit.return_value": mock_query,
        "get.return_value": [1]
    })
    mock_ref.configure_mock(**{
        "where.return_value": mock_query,
    })
    mdi_url = "100"

    fa = FirestoreAccessor()
    res = fa.url_exists(mdi_url)
    mock_ref.where.assert_called_once_with("url", "==", mdi_url)
    mock_query.limit.assert_called_once_with(1)
    mock_query.get.assert_called_once_with()

    assert res == True

def test_url_exists_doesnt_exist(mock_ref):
    mock_query = MagicMock()
    mock_query.configure_mock(**{
        "limit.return_value": mock_query,
        "get.return_value": []
    })
    mock_ref.configure_mock(**{
        "where.return_value": mock_query,
    })
    mdi_url = "100"

    fa = FirestoreAccessor()
    res = fa.url_exists(mdi_url)
    mock_ref.where.assert_called_once_with("url", "==", mdi_url)
    mock_query.limit.assert_called_once_with(1)
    mock_query.get.assert_called_once_with()

    assert res == False

def test_delete_metadata(mock_ref):
    mock_doc = MagicMock(exists=True)
    mock_ref.configure_mock(**{
        "document.return_value": mock_doc,
    })
    mdi_id = "fdsafkldjsklf"

    fa = FirestoreAccessor()
    fa.delete_metadata(mdi_id)
    mock_ref.document.assert_called_once_with(mdi_id)
    mock_doc.delete.assert_called_once_with()

def test_delete_metadata_not_exists(mock_ref):
    mock_doc = MagicMock(exists=False)
    mock_ref.configure_mock(**{
        "document.return_value": mock_doc,
    })
    mdi_id = "fdsafkldjsklf"

    fa = FirestoreAccessor()
    with pytest.raises(NotExistingException):
        fa.delete_metadata(mdi_id)
    
    mock_ref.document.assert_called_once_with(mdi_id)