from typing import Optional, List, Dict, Any, Union
from ..nocodb import (
    NocoDBClient,
    NocoDBProject,
    NocoDBBase,
    AuthToken,
    WhereFilter,
)
from ..api import NocoDBAPI
from ..utils import get_query_params
from ..exceptions import NocoDBAPIError

import requests


class NocoDBRequestsClient(NocoDBClient):
    def __init__(self, auth_token: AuthToken, base_uri: str):
        self.__session = requests.Session()
        self.__session.headers.update(
            auth_token.get_header(),
        )
        self.__session.headers.update({"Content-Type": "application/json"})
        self.__api_info = NocoDBAPI(base_uri)

    def _request(self, method: str, url: str, *args, **kwargs):
        response = self.__session.request(method, url, *args, **kwargs)
        response_json = None
        try:
            response.raise_for_status()
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            ...
        except requests.exceptions.HTTPError as http_error:
            raise NocoDBAPIError(
                message=str(http_error),
                status_code=http_error.response.status_code,
                response_json=response_json,
                response_text=response.text
            )

        return response

    def table_row_list(
        self,
        project: NocoDBProject,
        table: str,
        filter_obj: Optional[WhereFilter] = None,
        params: Optional[dict] = None,
    ) -> dict:
        return self._request(
            "GET",
            self.__api_info.get_table_uri(project, table),
            params=get_query_params(filter_obj, params),
        ).json()

    def table_row_create(self, project: NocoDBProject, table: str, body: dict) -> dict:
        return self._request(
            "POST", self.__api_info.get_table_uri(project, table), json=body
        ).json()

    def table_row_detail(self, project: NocoDBProject, table: str, row_id: int) -> dict:
        return self._request(
            "GET",
            self.__api_info.get_row_detail_uri(project, table, row_id),
        ).json()

    def table_row_update(
        self, project: NocoDBProject, table: str, row_id: int, body: dict
    ) -> dict:
        return self._request(
            "PATCH",
            self.__api_info.get_row_detail_uri(project, table, row_id),
            json=body,
        ).json()

    def table_row_delete(self, project: NocoDBProject, table: str, row_id: int) -> int:
        return self._request(
            "DELETE",
            self.__api_info.get_row_detail_uri(project, table, row_id),
        ).json()

    def table_count(
        self,
        project: NocoDBProject,
        table: str,
        filter_obj: Optional[WhereFilter] = None,
    ) -> dict:
        return self._request(
            "GET",
            self.__api_info.get_table_count_uri(project, table),
            params=get_query_params(filter_obj),
        ).json()

    def table_find_one(
        self,
        project: NocoDBProject,
        table: str,
        filter_obj: Optional[WhereFilter] = None,
        params: Optional[dict] = None,
    ) -> dict:
        return self._request(
            "GET",
            self.__api_info.get_table_find_one_uri(project, table),
            params=get_query_params(filter_obj, params),
        ).json()

    def table_row_nested_relations_list(
        self,
        project: NocoDBProject,
        table: str,
        relation_type: str,
        row_id: int,
        column_name: str,
    ) -> dict:
        return self._request(
            "GET",
            self.__api_info.get_nested_relations_rows_list_uri(
                project, table, relation_type, row_id, column_name
            ),
        ).json()

    def project_create(self, body):
        return self._request(
            "POST", self.__api_info.get_project_uri(), json=body
        ).json()

    def table_create(
        self, project: NocoDBProject, body: dict
    ) -> dict:
        return self._request(
            "POST",
            url=self.__api_info.get_project_tables_uri(project),
            json=body,
        ).json()

    def table_list(
        self,
        project: NocoDBProject,
        params: Optional[dict] = None,
    ) -> dict:
        return self._request(
            "GET",
            url=self.__api_info.get_project_tables_uri(project),
            params=params,
        ).json()

    def table_read(
        self, tableId: str,
    ) -> dict:
        return self._request(
            "GET",
            url=self.__api_info.get_table_meta_uri(tableId)
        ).json()

    def table_update(
        self, tableId: str, body: dict
    ):
        return self._request(
            "PATCH",
            url=self.__api_info.get_table_meta_uri(tableId),
            json=body,
        ).json()

    def table_delete(
        self, tableId: str,
    ) -> dict:
        return self._request(
            "DELETE",
            url=self.__api_info.get_table_meta_uri(tableId)
        ).json()

    def table_reorder(
        self, tableId: str, order: int
    ) -> dict:
        return self._request(
            "POST",
            url=self.__api_info.get_table_meta_uri(tableId, "reorder"),
            json={ "order": order }
        ).json()
    
    def table_column_create(
        self, tableId: str, body: dict,
    ) -> dict:
        return self._request(
            "POST",
            url=self.__api_info.get_table_meta_uri(tableId, "columns"),
            json=body,
        ).json()

    def table_column_update(
        self, columnId: str, body: dict,
    ) -> dict:
        return self._request(
            "PATCH",
            url=self.__api_info.get_column_uri(columnId),
            json=body,
        ).json()

    def table_column_delete(
        self, columnId: str,
    ) -> dict:
        return self._request(
            "DELETE",
            url=self.__api_info.get_column_uri(columnId)
        ).json()

    def table_column_set_primary(
        self, columnId: str,
    ) -> bool:
        return self._request(
            "POST",
            url=self.__api_info.get_column_uri(columnId, "primary"),
        ).json()

    # =========================================================================
    # v3 Data API Methods
    # =========================================================================

    def records_list_v3(
        self,
        base_id: str,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List records using v3 API.

        GET /api/v3/data/{baseId}/{tableId}/records

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            params: Optional query parameters:
                - fields: Comma-separated field names to include
                - sort: Sort field(s), prefix with - for descending
                - where: Filter condition
                - page: Page number (1-indexed)
                - pageSize: Number of records per page
                - viewId: Optional view ID to filter by

        Returns:
            Dict with 'records' array and optional 'next' pagination URL
            Example: {"records": [{"id": 1, "fields": {...}}], "next": "url"}
        """
        url = self.__api_info.get_records_uri(base_id, table_id)
        return self._request("GET", url, params=params).json()

    def record_get_v3(
        self,
        base_id: str,
        table_id: str,
        record_id: Union[int, str],
    ) -> Dict[str, Any]:
        """Get a single record using v3 API.

        GET /api/v3/data/{baseId}/{tableId}/records/{recordId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            record_id: The record ID

        Returns:
            Dict with 'id' and 'fields'
            Example: {"id": 1, "fields": {"Name": "John", "Age": 30}}
        """
        url = self.__api_info.get_record_uri(base_id, table_id, str(record_id))
        return self._request("GET", url).json()

    def records_create_v3(
        self,
        base_id: str,
        table_id: str,
        records: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Create one or more records using v3 API.

        POST /api/v3/data/{baseId}/{tableId}/records

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            records: Single record dict or list of record dicts
                Each record should have a 'fields' key with field values
                Example: {"fields": {"Name": "John"}} or
                         [{"fields": {"Name": "John"}}, {"fields": {"Name": "Jane"}}]

        Returns:
            List of created records with 'id' and 'fields'
            Example: [{"id": 1, "fields": {"Name": "John"}}]
        """
        url = self.__api_info.get_records_uri(base_id, table_id)

        # Normalize to list format for API
        if isinstance(records, dict):
            body = [records]
        else:
            body = records

        return self._request("POST", url, json=body).json()

    def records_update_v3(
        self,
        base_id: str,
        table_id: str,
        records: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Update one or more records using v3 API.

        PATCH /api/v3/data/{baseId}/{tableId}/records

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            records: Single record dict or list of record dicts
                Each record must have 'id' and 'fields' keys
                Example: {"id": 1, "fields": {"Name": "Updated"}} or
                         [{"id": 1, "fields": {...}}, {"id": 2, "fields": {...}}]

        Returns:
            List of updated records with 'id' and 'fields'
            Example: [{"id": 1, "fields": {"Name": "Updated"}}]
        """
        url = self.__api_info.get_records_uri(base_id, table_id)

        # Normalize to list format for API
        if isinstance(records, dict):
            body = [records]
        else:
            body = records

        return self._request("PATCH", url, json=body).json()

    def records_delete_v3(
        self,
        base_id: str,
        table_id: str,
        record_ids: Union[int, str, List[Union[int, str]]],
    ) -> List[Dict[str, Any]]:
        """Delete one or more records using v3 API.

        DELETE /api/v3/data/{baseId}/{tableId}/records

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            record_ids: Single record ID or list of record IDs to delete

        Returns:
            List of deleted record IDs
            Example: [{"id": 1}, {"id": 2}]
        """
        url = self.__api_info.get_records_uri(base_id, table_id)

        # Normalize to list format for API
        if isinstance(record_ids, (int, str)):
            body = [{"id": record_ids}]
        else:
            body = [{"id": rid} for rid in record_ids]

        return self._request("DELETE", url, json=body).json()

    def records_count_v3(
        self,
        base_id: str,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """Get record count using v3 API.

        GET /api/v3/data/{baseId}/{tableId}/count

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            params: Optional query parameters (e.g., where filter)

        Returns:
            Dict with 'count' key
            Example: {"count": 42}
        """
        url = self.__api_info.get_records_count_uri(base_id, table_id)
        return self._request("GET", url, params=params).json()
