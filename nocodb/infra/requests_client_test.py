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
    """Test that bases_list_v3 calls the correct v3 API endpoint."""
    mock_session = mock.Mock()
    mock_requests_session.return_value = mock_session

    expected_response = {"bases": [{"id": "base_abc", "title": "My Base"}]}
    mock_session.request.return_value = _create_mock_response(200, expected_response)

    token = APIToken("test-token")
    client = NocoDBRequestsClient(token, "https://app.nocodb.com")

    result = client.bases_list_v3()

    call_args = mock_session.request.call_args
    assert call_args[0][0] == "GET"
    # v3 API path for listing bases (without workspace for self-hosted)
    assert "/api/v3/meta/bases" in call_args[0][1]
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
