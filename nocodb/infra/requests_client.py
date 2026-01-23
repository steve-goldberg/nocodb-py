import warnings
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
        """Create a table in a project (DEPRECATED).

        .. deprecated:: 3.0.0
            Use :meth:`table_create_v3` with base_id instead.
        """
        warnings.warn(
            "table_create() is deprecated. Use table_create_v3(base_id, body) instead.",
            DeprecationWarning,
            stacklevel=2
        )
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
        """List tables in a project (DEPRECATED).

        .. deprecated:: 3.0.0
            Use :meth:`tables_list_v3` with base_id instead.
        """
        warnings.warn(
            "table_list() is deprecated. Use tables_list_v3(base_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._request(
            "GET",
            url=self.__api_info.get_project_tables_uri(project),
            params=params,
        ).json()

    def table_read(
        self, tableId: str,
    ) -> dict:
        """Read a table's metadata (DEPRECATED).

        .. deprecated:: 3.0.0
            Use :meth:`table_read_v3` with base_id and table_id instead.
        """
        warnings.warn(
            "table_read() is deprecated. Use table_read_v3(base_id, table_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._request(
            "GET",
            url=self.__api_info.get_table_meta_uri(tableId)
        ).json()

    def table_update(
        self, tableId: str, body: dict
    ):
        """Update a table's metadata (DEPRECATED).

        .. deprecated:: 3.0.0
            Use :meth:`table_update_v3` with base_id and table_id instead.
        """
        warnings.warn(
            "table_update() is deprecated. Use table_update_v3(base_id, table_id, body) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._request(
            "PATCH",
            url=self.__api_info.get_table_meta_uri(tableId),
            json=body,
        ).json()

    def table_delete(
        self, tableId: str,
    ) -> dict:
        """Delete a table (DEPRECATED).

        .. deprecated:: 3.0.0
            Use :meth:`table_delete_v3` with base_id and table_id instead.
        """
        warnings.warn(
            "table_delete() is deprecated. Use table_delete_v3(base_id, table_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._request(
            "DELETE",
            url=self.__api_info.get_table_meta_uri(tableId)
        ).json()

    def table_reorder(
        self, tableId: str, order: int
    ) -> dict:
        """Reorder a table (DEPRECATED - not available in v3 API).

        .. deprecated:: 3.0.0
            This method uses v1 API and is not available in v3 API.
            Table ordering in v3 is managed differently.
        """
        warnings.warn(
            "table_reorder() is deprecated and not available in v3 API.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._request(
            "POST",
            url=self.__api_info.get_table_meta_uri(tableId, "reorder"),
            json={"order": order}
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

    def records_list_all_v3(
        self,
        base_id: str,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
        max_pages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """List ALL records from a table, automatically handling pagination.

        This method fetches all pages of records from a table, following the
        'next' URL returned by the v3 API until no more pages are available.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            params: Optional query parameters (pageSize, where, sort, etc.)
            max_pages: Optional limit on pages to fetch (None = unlimited)

        Returns:
            List of all records (may be large!)
            Each record has 'id' and 'fields' keys.

        Example:
            all_users = client.records_list_all_v3(base_id, table_id, params={
                "pageSize": 100,
                "where": "(Status,eq,Active)"
            })
        """
        from ..utils import collect_all_v3

        def fetch(p: Dict[str, Any]) -> Dict[str, Any]:
            merged_params = dict(params or {})
            merged_params.update(p)
            return self.records_list_v3(base_id, table_id, params=merged_params)

        return collect_all_v3(fetch, params, max_pages)

    def linked_records_list_v3(
        self,
        base_id: str,
        table_id: str,
        link_field_id: str,
        record_id: Union[int, str],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List linked records for a specific record using v3 API.

        GET /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            link_field_id: The link field ID
            record_id: The record ID
            params: Optional query parameters:
                - fields: Comma-separated field names to include
                - sort: Sort field(s), prefix with - for descending
                - where: Filter condition
                - page: Page number (1-indexed)
                - pageSize: Number of records per page

        Returns:
            Dict with 'list' array of linked records and optional 'next' pagination URL
            Example: {"list": [{"id": 1, "fields": {...}}], "next": "url"}
        """
        url = self.__api_info.get_linked_records_uri(base_id, table_id, link_field_id, str(record_id))
        return self._request("GET", url, params=params).json()

    # =========================================================================
    # v3 Meta API Methods
    # =========================================================================

    def workspaces_list_v3(
        self,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List workspaces using v3 API (Enterprise feature).

        GET /api/v3/meta/workspaces

        Args:
            params: Optional query parameters

        Returns:
            Dict with 'workspaces' array
            Example: {"workspaces": [{"id": "ws_abc", "title": "My Workspace"}]}
        """
        url = self.__api_info.get_workspaces_uri()
        return self._request("GET", url, params=params).json()

    def bases_list_v3(
        self,
        workspace_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List bases using v2 API (v3 is Enterprise-only).

        Note: Despite the method name, this uses v2 API because v3 bases list
        is Enterprise-only and not available in self-hosted NocoDB.

        GET /api/v2/meta/bases

        Args:
            workspace_id: Ignored for self-hosted (no workspaces in community edition)
            params: Optional query parameters

        Returns:
            Dict with 'list' array of bases
            Example: {"list": [{"id": "base_abc", "title": "My Base"}]}
        """
        # Use v2 API - v3 bases list is Enterprise-only
        url = self.__api_info.get_bases_list_uri_v2()
        return self._request("GET", url, params=params).json()

    def bases_list(
        self,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all bases using v2 API (for self-hosted NocoDB).

        GET /api/v2/meta/bases

        Note: This uses v2 API because v3 bases list is Enterprise-only.
        Self-hosted NocoDB community edition must use this endpoint.

        Args:
            params: Optional query parameters

        Returns:
            Dict with 'list' array of bases
            Example: {"list": [{"id": "...", "title": "...", ...}]}
        """
        url = self.__api_info.get_bases_list_uri_v2()
        return self._request("GET", url, params=params).json()

    def tables_list_v3(
        self,
        base_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List tables in a base using v3 API.

        GET /api/v3/meta/bases/{baseId}/tables

        Args:
            base_id: The base (project) ID
            params: Optional query parameters

        Returns:
            Dict with 'tables' array
            Example: {"tables": [{"id": "tbl_abc", "title": "My Table"}]}
        """
        url = self.__api_info.get_tables_uri(base_id)
        return self._request("GET", url, params=params).json()

    def table_create_v3(
        self,
        base_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new table using v3 API.

        POST /api/v3/meta/bases/{baseId}/tables

        Args:
            base_id: The base (project) ID
            body: Table configuration (title, columns, etc.)
                Example: {"title": "MyTable", "columns": [...]}

        Returns:
            Created table object with id, title, etc.
        """
        url = self.__api_info.get_tables_uri(base_id)
        return self._request("POST", url, json=body).json()

    def table_read_v3(
        self,
        base_id: str,
        table_id: str,
    ) -> Dict[str, Any]:
        """Read a single table's metadata using v3 API.

        GET /api/v3/meta/bases/{baseId}/tables/{tableId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID

        Returns:
            Table object with id, title, columns, etc.
        """
        url = self.__api_info.get_table_meta_uri_v3(base_id, table_id)
        return self._request("GET", url).json()

    def table_update_v3(
        self,
        base_id: str,
        table_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a table's metadata using v3 API.

        PATCH /api/v3/meta/bases/{baseId}/tables/{tableId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            body: Fields to update (e.g., {"title": "NewName"})

        Returns:
            Updated table object
        """
        url = self.__api_info.get_table_meta_uri_v3(base_id, table_id)
        return self._request("PATCH", url, json=body).json()

    def table_delete_v3(
        self,
        base_id: str,
        table_id: str,
    ) -> Dict[str, Any]:
        """Delete a table using v3 API.

        DELETE /api/v3/meta/bases/{baseId}/tables/{tableId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_table_meta_uri_v3(base_id, table_id)
        return self._request("DELETE", url).json()

    # =========================================================================
    # v3 Meta API Methods - API Tokens
    # =========================================================================

    def tokens_list(
        self,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all API tokens.

        GET /api/v3/meta/tokens

        Args:
            params: Optional query parameters

        Returns:
            Dict with 'tokens' array
            Example: {"tokens": [{"id": "...", "token": "nc_...", "description": "..."}]}
        """
        url = self.__api_info.get_tokens_uri()
        return self._request("GET", url, params=params).json()

    def token_create(
        self,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new API token.

        POST /api/v3/meta/tokens

        Args:
            body: Token configuration with 'description' key
                Example: {"description": "My API Token"}

        Returns:
            Created token object with 'id', 'token', and 'description'
            Example: {"id": "...", "token": "nc_...", "description": "My API Token"}
        """
        url = self.__api_info.get_tokens_uri()
        return self._request("POST", url, json=body).json()

    def token_delete(
        self,
        token_id: str,
    ) -> Any:
        """Delete an API token.

        DELETE /api/v3/meta/tokens/{tokenId}

        Args:
            token_id: The API token ID

        Returns:
            Deletion confirmation (may be empty or boolean)
        """
        url = self.__api_info.get_token_uri(token_id)
        response = self._request("DELETE", url)
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return True
