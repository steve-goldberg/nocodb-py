from unittest import mock
import json

import pytest
import requests

from .requests_client import NocoDBRequestsClient, requests as requests_lib
from ..exceptions import NocoDBAPIError
from ..nocodb import APIToken


@mock.patch.object(requests_lib, "Session")
def test_NocoDBAPIError_raised_on_bad_response(mock_requests_session):
    mock_session = mock.Mock()
    mock_resp = requests.models.Response()
    mock_resp.status_code = 401
    mock_requests_session.return_value = mock_session
    mock_session.request.return_value = mock_resp

    client = NocoDBRequestsClient(mock.Mock(), "")
    with pytest.raises(NocoDBAPIError) as exc_info:
        client._request("GET", "/")

    assert exc_info.value.status_code == 401


# =========================================================================
# v3 API Tests
# =========================================================================


def _create_mock_response(status_code: int, json_data: dict):
    """Helper to create a mock response."""
    mock_resp = mock.Mock(spec=requests.models.Response)
    mock_resp.status_code = status_code
    mock_resp.json.return_value = json_data
    mock_resp.raise_for_status = mock.Mock()
    return mock_resp


@mock.patch.object(requests_lib, "Session")
def test_records_list_v3_calls_correct_url(mock_requests_session):
    """Test that records_list_v3 calls the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"records": [{"id": 1, "fields": {"Name": "Test"}}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.records_list_v3("base123", "tbl456")

    # Verify the correct URL was called
    mock_session.request.assert_called_once()
    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/data/base123/tbl456/records" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_list_v3_with_params(mock_requests_session):
    """Test that records_list_v3 passes query parameters correctly."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"records": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    params = {"where": "(Status,eq,active)", "pageSize": 10}
    client.records_list_v3("base123", "tbl456", params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"] == params


@mock.patch.object(requests_lib, "Session")
def test_record_get_v3_calls_correct_url(mock_requests_session):
    """Test that record_get_v3 calls the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": 42, "fields": {"Name": "Test"}}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.record_get_v3("base123", "tbl456", 42)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/data/base123/tbl456/records/42" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_create_v3_single_record(mock_requests_session):
    """Test that records_create_v3 handles single record creation."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 1, "fields": {"Name": "New"}}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    record = {"fields": {"Name": "New"}}
    result = client.records_create_v3("base123", "tbl456", record)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    assert "/api/v3/data/base123/tbl456/records" in call_args[0][1]
    # Single record should be wrapped in array
    assert call_args[1]["json"] == [record]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_create_v3_multiple_records(mock_requests_session):
    """Test that records_create_v3 handles multiple record creation."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [
        {"id": 1, "fields": {"Name": "First"}},
        {"id": 2, "fields": {"Name": "Second"}}
    ]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    records = [
        {"fields": {"Name": "First"}},
        {"fields": {"Name": "Second"}}
    ]
    result = client.records_create_v3("base123", "tbl456", records)

    call_args = mock_session.request.call_args
    assert call_args[1]["json"] == records
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_update_v3(mock_requests_session):
    """Test that records_update_v3 calls PATCH with correct format."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 1, "fields": {"Name": "Updated"}}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    record = {"id": 1, "fields": {"Name": "Updated"}}
    result = client.records_update_v3("base123", "tbl456", record)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "PATCH"
    assert "/api/v3/data/base123/tbl456/records" in call_args[0][1]
    assert call_args[1]["json"] == [record]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_delete_v3_single_id(mock_requests_session):
    """Test that records_delete_v3 handles single record deletion."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 1}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.records_delete_v3("base123", "tbl456", 1)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v3/data/base123/tbl456/records" in call_args[0][1]
    assert call_args[1]["json"] == [{"id": 1}]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_delete_v3_multiple_ids(mock_requests_session):
    """Test that records_delete_v3 handles multiple record deletion."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 1}, {"id": 2}, {"id": 3}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.records_delete_v3("base123", "tbl456", [1, 2, 3])

    call_args = mock_session.request.call_args
    assert call_args[1]["json"] == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_count_v3(mock_requests_session):
    """Test that records_count_v3 calls the correct endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"count": 42}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.records_count_v3("base123", "tbl456")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/data/base123/tbl456/count" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_records_count_v3_with_filter(mock_requests_session):
    """Test that records_count_v3 passes filter parameters."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"count": 10}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    params = {"where": "(Status,eq,active)"}
    result = client.records_count_v3("base123", "tbl456", params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"] == params
    assert result == expected_response


# =========================================================================
# v3 Meta API Tests
# =========================================================================


@mock.patch.object(requests_lib, "Session")
def test_tables_list_v3_calls_correct_url(mock_requests_session):
    """Test that tables_list_v3 calls the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"tables": [{"id": "tbl_abc", "title": "Users"}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.tables_list_v3("base123")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/meta/bases/base123/tables" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_tables_list_v3_with_params(mock_requests_session):
    """Test that tables_list_v3 passes query parameters correctly."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"tables": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    params = {"includeM2M": True}
    client.tables_list_v3("base123", params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"] == params


@mock.patch.object(requests_lib, "Session")
def test_bases_list_v3_calls_correct_url(mock_requests_session):
    """Test that bases_list_v3 calls the v2 API endpoint (v3 is Enterprise-only)."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": [{"id": "base_abc", "title": "My Base"}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.bases_list_v3()

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    # Uses v2 API - v3 bases list is Enterprise-only
    assert "/api/v2/meta/bases" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_bases_list_calls_correct_url(mock_requests_session):
    """Test that bases_list calls the v2 API endpoint for self-hosted NocoDB."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": [{"id": "base_abc", "title": "My Base"}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.bases_list()

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    # v2 API for self-hosted NocoDB community edition
    assert "/api/v2/meta/bases" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_base_create_calls_correct_url(mock_requests_session):
    """Test that base_create calls POST on v2 API endpoint (v3 is Enterprise-only)."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "base_new", "title": "My New Base"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "My New Base"}
    result = client.base_create(body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    # Uses v2 API - v3 base creation is Enterprise-only
    assert "/api/v2/meta/bases" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_base_read_calls_correct_url(mock_requests_session):
    """Test that base_read calls GET on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "base123", "title": "My Base", "tables": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.base_read("base123")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/meta/bases/base123" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_base_update_calls_correct_url(mock_requests_session):
    """Test that base_update calls PATCH on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "base123", "title": "Renamed Base"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "Renamed Base"}
    result = client.base_update("base123", body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "PATCH"
    assert "/api/v3/meta/bases/base123" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_base_delete_calls_correct_url(mock_requests_session):
    """Test that base_delete calls DELETE on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"success": True}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.base_delete("base123")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v3/meta/bases/base123" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_table_create_v3_calls_correct_url(mock_requests_session):
    """Test that table_create_v3 calls POST on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "tbl_new", "title": "NewTable"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "NewTable", "columns": [{"title": "Name", "uidt": "SingleLineText"}]}
    result = client.table_create_v3("base123", body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    assert "/api/v3/meta/bases/base123/tables" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_table_read_v3_calls_correct_url(mock_requests_session):
    """Test that table_read_v3 calls GET on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "tbl_abc", "title": "Users", "columns": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.table_read_v3("base123", "tbl_abc")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/meta/bases/base123/tables/tbl_abc" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_table_update_v3_calls_correct_url(mock_requests_session):
    """Test that table_update_v3 calls PATCH on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "tbl_abc", "title": "RenamedTable"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "RenamedTable"}
    result = client.table_update_v3("base123", "tbl_abc", body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "PATCH"
    assert "/api/v3/meta/bases/base123/tables/tbl_abc" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_table_delete_v3_calls_correct_url(mock_requests_session):
    """Test that table_delete_v3 calls DELETE on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"success": True}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.table_delete_v3("base123", "tbl_abc")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v3/meta/bases/base123/tables/tbl_abc" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_linked_records_list_v3_calls_correct_url(mock_requests_session):
    """Test that linked_records_list_v3 calls the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": [{"id": 1, "fields": {"Name": "Linked Record"}}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.linked_records_list_v3("base123", "tbl456", "fld_link", 42)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/data/base123/tbl456/links/fld_link/42" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_linked_records_list_v3_with_params(mock_requests_session):
    """Test that linked_records_list_v3 passes query parameters correctly."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    params = {"pageSize": 10, "sort": "-created_at"}
    client.linked_records_list_v3("base123", "tbl456", "fld_link", 42, params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"] == params


@mock.patch.object(requests_lib, "Session")
def test_linked_records_link_v3_single_id(mock_requests_session):
    """Test that linked_records_link_v3 handles single record linking."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 10}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.linked_records_link_v3("base123", "tbl456", "fld_link", 42, 10)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    assert "/api/v3/data/base123/tbl456/links/fld_link/42" in call_args[0][1]
    assert call_args[1]["json"] == [{"id": 10}]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_linked_records_link_v3_multiple_ids(mock_requests_session):
    """Test that linked_records_link_v3 handles multiple record linking."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 10}, {"id": 20}, {"id": 30}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.linked_records_link_v3("base123", "tbl456", "fld_link", 42, [10, 20, 30])

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    assert "/api/v3/data/base123/tbl456/links/fld_link/42" in call_args[0][1]
    assert call_args[1]["json"] == [{"id": 10}, {"id": 20}, {"id": 30}]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_linked_records_link_v3_string_ids(mock_requests_session):
    """Test that linked_records_link_v3 handles string record IDs."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": "rec_abc"}, {"id": "rec_def"}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.linked_records_link_v3("base123", "tbl456", "fld_link", "rec_main", ["rec_abc", "rec_def"])

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    assert "/api/v3/data/base123/tbl456/links/fld_link/rec_main" in call_args[0][1]
    assert call_args[1]["json"] == [{"id": "rec_abc"}, {"id": "rec_def"}]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_linked_records_unlink_v3_single_id(mock_requests_session):
    """Test that linked_records_unlink_v3 handles single record unlinking."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 5}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.linked_records_unlink_v3("base123", "tbl456", "fld_link", 42, 5)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v3/data/base123/tbl456/links/fld_link/42" in call_args[0][1]
    assert call_args[1]["json"] == [{"id": 5}]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_linked_records_unlink_v3_multiple_ids(mock_requests_session):
    """Test that linked_records_unlink_v3 handles multiple record unlinking."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": 5}, {"id": 6}, {"id": 7}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.linked_records_unlink_v3("base123", "tbl456", "fld_link", 42, [5, 6, 7])

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v3/data/base123/tbl456/links/fld_link/42" in call_args[0][1]
    assert call_args[1]["json"] == [{"id": 5}, {"id": 6}, {"id": 7}]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_linked_records_unlink_v3_with_string_ids(mock_requests_session):
    """Test that linked_records_unlink_v3 handles string record IDs."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = [{"id": "rec_abc"}]
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.linked_records_unlink_v3("base123", "tbl456", "fld_link", "rec_123", "rec_abc")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v3/data/base123/tbl456/links/fld_link/rec_123" in call_args[0][1]
    assert call_args[1]["json"] == [{"id": "rec_abc"}]
    assert result == expected_response


# =========================================================================
# v3 Filter Integration Tests
# =========================================================================


@mock.patch.object(requests_lib, "Session")
def test_records_list_v3_with_v3_filter_operators(mock_requests_session):
    """Test v3 filter operators (gte, lte) are passed correctly."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"records": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    # v3 uses gte/lte (not ge/le)
    params = {"where": "(age,gte,18)~and(age,lte,65)"}
    client.records_list_v3("base123", "tbl456", params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"]["where"] == "(age,gte,18)~and(age,lte,65)"


@mock.patch.object(requests_lib, "Session")
def test_records_list_v3_with_v3_logical_operators(mock_requests_session):
    """Test v3 logical operators (~and, ~or) are passed correctly."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"records": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    # v3 uses ~and, ~or (no outer parentheses)
    params = {"where": "(status,eq,active)~or(status,eq,pending)"}
    client.records_list_v3("base123", "tbl456", params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"]["where"] == "(status,eq,active)~or(status,eq,pending)"


# =========================================================================
# v3 Meta API Tests - Fields
# =========================================================================


@mock.patch.object(requests_lib, "Session")
def test_fields_list_v3_calls_correct_url(mock_requests_session):
    """Test that fields_list_v3 calls the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": [{"id": "fld_abc", "title": "Name", "uidt": "SingleLineText"}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.fields_list_v3("base123", "tbl456")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v3/meta/bases/base123/tables/tbl456/fields" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_fields_list_v3_with_params(mock_requests_session):
    """Test that fields_list_v3 passes query parameters correctly."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    params = {"includeSystem": True}
    client.fields_list_v3("base123", "tbl456", params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"] == params


@mock.patch.object(requests_lib, "Session")
def test_field_create_v3_calls_correct_url(mock_requests_session):
    """Test that field_create_v3 calls POST on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "fld_new", "title": "Email", "uidt": "Email"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "Email", "uidt": "Email"}
    result = client.field_create_v3("base123", "tbl456", body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    assert "/api/v3/meta/bases/base123/tables/tbl456/fields" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_field_update_v3_calls_correct_url(mock_requests_session):
    """Test that field_update_v3 calls PATCH on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "fld_abc", "title": "RenamedField"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "RenamedField"}
    result = client.field_update_v3("base123", "fld_abc", body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "PATCH"
    assert "/api/v3/meta/bases/base123/fields/fld_abc" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_field_delete_v3_calls_correct_url(mock_requests_session):
    """Test that field_delete_v3 calls DELETE on the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"success": True}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.field_delete_v3("base123", "fld_abc")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v3/meta/bases/base123/fields/fld_abc" in call_args[0][1]
    assert result == expected_response


# =========================================================================
# Backwards Compatibility Alias Tests (column -> field)
# =========================================================================


@mock.patch.object(requests_lib, "Session")
def test_columns_list_v3_alias_emits_warning(mock_requests_session):
    """Test that columns_list_v3 alias emits deprecation warning."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = client.columns_list_v3("base123", "tbl456")
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "columns_list_v3() is deprecated" in str(w[0].message)

    # Verify it still works correctly
    call_args = mock_session.request.call_args
    assert "/api/v3/meta/bases/base123/tables/tbl456/fields" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_column_create_v3_alias_emits_warning(mock_requests_session):
    """Test that column_create_v3 alias emits deprecation warning."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "fld_new"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = client.column_create_v3("base123", "tbl456", {"title": "Test"})
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "column_create_v3() is deprecated" in str(w[0].message)

    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_column_update_v3_alias_emits_warning(mock_requests_session):
    """Test that column_update_v3 alias emits deprecation warning."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "fld_abc"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = client.column_update_v3("base123", "fld_abc", {"title": "Test"})
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "column_update_v3() is deprecated" in str(w[0].message)

    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_column_delete_v3_alias_emits_warning(mock_requests_session):
    """Test that column_delete_v3 alias emits deprecation warning."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"success": True}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = client.column_delete_v3("base123", "fld_abc")
        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)
        assert "column_delete_v3() is deprecated" in str(w[0].message)

    assert result == expected_response


# =========================================================================
# v2 Meta API Tests - Views
# =========================================================================


@mock.patch.object(requests_lib, "Session")
def test_views_list_calls_correct_url(mock_requests_session):
    """Test that views_list calls the correct v2 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": [{"id": "vw_abc", "title": "Grid View", "type": 3}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.views_list("tbl123")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v2/meta/tables/tbl123/views" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_views_list_with_params(mock_requests_session):
    """Test that views_list passes query parameters correctly."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"list": []}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    params = {"includeM2M": True}
    client.views_list("tbl123", params=params)

    call_args = mock_session.request.call_args
    assert call_args[1]["params"] == params


@mock.patch.object(requests_lib, "Session")
def test_view_create_calls_correct_url(mock_requests_session):
    """Test that view_create calls POST on the correct v2 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "vw_new", "title": "My Grid View", "type": 3}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "My Grid View", "type": 3}
    result = client.view_create("tbl123", body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "POST"
    assert "/api/v2/meta/tables/tbl123/views" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_view_create_different_types(mock_requests_session):
    """Test that view_create works with different view types."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    # Test creating a form view (type: 5)
    expected_response = {"id": "vw_form", "title": "Contact Form", "type": 5}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "Contact Form", "type": 5}
    result = client.view_create("tbl123", body)

    call_args = mock_session.request.call_args
    assert call_args[1]["json"] == body
    assert result["type"] == 5


@mock.patch.object(requests_lib, "Session")
def test_view_read_calls_correct_url(mock_requests_session):
    """Test that view_read calls GET on the correct v2 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "vw_abc", "title": "Grid View", "type": 3}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.view_read("vw_abc")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    assert "/api/v2/meta/views/vw_abc" in call_args[0][1]
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_view_update_calls_correct_url(mock_requests_session):
    """Test that view_update calls PATCH on the correct v2 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"id": "vw_abc", "title": "Renamed View"}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    body = {"title": "Renamed View"}
    result = client.view_update("vw_abc", body)

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "PATCH"
    assert "/api/v2/meta/views/vw_abc" in call_args[0][1]
    assert call_args[1]["json"] == body
    assert result == expected_response


@mock.patch.object(requests_lib, "Session")
def test_view_delete_calls_correct_url(mock_requests_session):
    """Test that view_delete calls DELETE on the correct v2 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"success": True}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.view_delete("vw_abc")

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "DELETE"
    assert "/api/v2/meta/views/vw_abc" in call_args[0][1]
    assert result == expected_response
