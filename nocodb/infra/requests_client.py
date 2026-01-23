import base64
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

    def linked_records_link_v3(
        self,
        base_id: str,
        table_id: str,
        link_field_id: str,
        record_id: Union[int, str],
        linked_record_ids: Union[int, str, List[Union[int, str]]],
    ) -> List[Dict[str, Any]]:
        """Link records to a specific record using v3 API.

        POST /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            link_field_id: The link field ID
            record_id: The record ID to link to
            linked_record_ids: Single record ID or list of record IDs to link

        Returns:
            List of linked record references
            Example: [{"id": 1}, {"id": 2}]
        """
        url = self.__api_info.get_linked_records_uri(base_id, table_id, link_field_id, str(record_id))

        # Normalize to list format for API
        if isinstance(linked_record_ids, (int, str)):
            body = [{"id": linked_record_ids}]
        else:
            body = [{"id": rid} for rid in linked_record_ids]

        return self._request("POST", url, json=body).json()

    def linked_records_unlink_v3(
        self,
        base_id: str,
        table_id: str,
        link_field_id: str,
        record_id: Union[int, str],
        linked_record_ids: Union[int, str, List[Union[int, str]]],
    ) -> List[Dict[str, Any]]:
        """Unlink records from a specific record using v3 API.

        DELETE /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            link_field_id: The link field ID
            record_id: The record ID to unlink from
            linked_record_ids: Single ID or list of IDs of records to unlink

        Returns:
            List of unlinked record IDs
            Example: [{"id": 1}, {"id": 2}]
        """
        url = self.__api_info.get_linked_records_uri(base_id, table_id, link_field_id, str(record_id))

        # Normalize to list format for API
        if isinstance(linked_record_ids, (int, str)):
            body = [{"id": linked_record_ids}]
        else:
            body = [{"id": rid} for rid in linked_record_ids]

        return self._request("DELETE", url, json=body).json()

    def button_action_trigger_v3(
        self,
        base_id: str,
        table_id: str,
        column_id: str,
        row_ids: List[Union[int, str]],
        preview: bool = False,
    ) -> List[Dict[str, Any]]:
        """Trigger button action on specified rows using v3 API.

        POST /api/v3/data/{baseId}/{tableId}/actions/{columnId}

        Supports Formula, Webhook, AI, and Script button types.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            column_id: The button column ID
            row_ids: List of record IDs to trigger action on (max 25 per request)
            preview: If True, preview mode - does not execute the action

        Returns:
            List of updated DataRecordV3 objects with 'id' and 'fields'
            Example: [{"id": 1, "fields": {"Name": "Updated"}}]

        Raises:
            ValueError: If row_ids contains more than 25 items
        """
        if len(row_ids) > 25:
            raise ValueError("Maximum 25 rows per button action request")

        url = self.__api_info.get_button_action_uri(base_id, table_id, column_id)
        body = {
            "rowIds": row_ids,
            "preview": preview
        }
        return self._request("POST", url, json=body).json()

    def attachment_upload_v3(
        self,
        base_id: str,
        table_id: str,
        record_id: Union[int, str],
        field_id: str,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> Dict[str, Any]:
        """Upload attachment to a record field using v3 API.

        POST /api/v3/data/{baseId}/{tableId}/records/{recordId}/fields/{fieldId}/upload

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            record_id: The record ID
            field_id: The attachment field ID
            filename: The filename for the uploaded file
            content: The file content as bytes
            content_type: The MIME type of the file (e.g., "image/png")

        Returns:
            The uploaded attachment metadata
            Example: {"url": "https://...", "title": "image.png", "mimetype": "image/png"}
        """
        url = self.__api_info.get_attachment_upload_uri(
            base_id, table_id, str(record_id), field_id
        )

        # Convert bytes content to base64
        file_base64 = base64.b64encode(content).decode("utf-8")

        body = {
            "contentType": content_type,
            "file": file_base64,
            "filename": filename
        }

        return self._request("POST", url, json=body).json()

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

    def base_create(
        self,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new base using v2 API.

        POST /api/v2/meta/bases

        Note: v3 base creation is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            body: Base configuration with 'title' key
                Example: {"title": "My New Base"}

        Returns:
            Created base object with id, title, etc.
            Example: {"id": "base_abc", "title": "My New Base", ...}
        """
        url = self.__api_info.get_base_create_uri_v2()
        return self._request("POST", url, json=body).json()

    def base_read(
        self,
        base_id: str,
    ) -> Dict[str, Any]:
        """Read a single base's metadata using v3 API.

        GET /api/v3/meta/bases/{baseId}

        Args:
            base_id: The base (project) ID

        Returns:
            Base object with id, title, tables, etc.
        """
        url = self.__api_info.get_base_uri(base_id)
        return self._request("GET", url).json()

    def base_update(
        self,
        base_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a base's metadata using v3 API.

        PATCH /api/v3/meta/bases/{baseId}

        Args:
            base_id: The base (project) ID
            body: Fields to update (e.g., {"title": "NewName"})

        Returns:
            Updated base object
        """
        url = self.__api_info.get_base_uri(base_id)
        return self._request("PATCH", url, json=body).json()

    def base_delete(
        self,
        base_id: str,
    ) -> Dict[str, Any]:
        """Delete a base using v3 API.

        DELETE /api/v3/meta/bases/{baseId}

        Args:
            base_id: The base (project) ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_base_uri(base_id)
        return self._request("DELETE", url).json()

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

    # =========================================================================
    # v3 Meta API Methods - Fields
    # =========================================================================

    def fields_list_v3(
        self,
        base_id: str,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all fields/columns in a table.

        GET /api/v3/meta/bases/{baseId}/tables/{tableId}/fields

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            params: Optional query parameters

        Returns:
            Dict with 'list' array of fields
            Example: {"list": [{"id": "fld_abc", "title": "Name", "uidt": "SingleLineText"}]}
        """
        url = self.__api_info.get_fields_uri(base_id, table_id)
        return self._request("GET", url, params=params).json()

    def field_create_v3(
        self,
        base_id: str,
        table_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new field/column in a table.

        POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            body: Field configuration (title, uidt, etc.)
                Example: {"title": "Email", "uidt": "Email"}

        Returns:
            Created field object with id, title, uidt, etc.
        """
        url = self.__api_info.get_fields_uri(base_id, table_id)
        return self._request("POST", url, json=body).json()

    def field_read_v3(
        self,
        base_id: str,
        field_id: str,
    ) -> Dict[str, Any]:
        """Get details of a specific field/column.

        GET /api/v3/meta/bases/{baseId}/fields/{fieldId}

        Args:
            base_id: The base (project) ID
            field_id: The field ID

        Returns:
            Field object with id, title, uidt, etc.
            Example: {"id": "fld_abc", "title": "Name", "uidt": "SingleLineText"}
        """
        url = self.__api_info.get_field_uri(base_id, field_id)
        return self._request("GET", url).json()

    def field_update_v3(
        self,
        base_id: str,
        field_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a field/column.

        PATCH /api/v3/meta/bases/{baseId}/fields/{fieldId}

        Args:
            base_id: The base (project) ID
            field_id: The field ID
            body: Fields to update (e.g., {"title": "NewName"})

        Returns:
            Updated field object
        """
        url = self.__api_info.get_field_uri(base_id, field_id)
        return self._request("PATCH", url, json=body).json()

    def field_delete_v3(
        self,
        base_id: str,
        field_id: str,
    ) -> Dict[str, Any]:
        """Delete a field/column.

        DELETE /api/v3/meta/bases/{baseId}/fields/{fieldId}

        Args:
            base_id: The base (project) ID
            field_id: The field ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_field_uri(base_id, field_id)
        return self._request("DELETE", url).json()

    # =========================================================================
    # Backwards Compatibility Aliases (column -> field)
    # =========================================================================

    def columns_list_v3(
        self,
        base_id: str,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Alias for fields_list_v3 (backwards compatibility).

        .. deprecated:: 3.0.0
            Use :meth:`fields_list_v3` instead.
        """
        warnings.warn(
            "columns_list_v3() is deprecated. Use fields_list_v3() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.fields_list_v3(base_id, table_id, params)

    def column_create_v3(
        self,
        base_id: str,
        table_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Alias for field_create_v3 (backwards compatibility).

        .. deprecated:: 3.0.0
            Use :meth:`field_create_v3` instead.
        """
        warnings.warn(
            "column_create_v3() is deprecated. Use field_create_v3() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.field_create_v3(base_id, table_id, body)

    def column_read_v3(
        self,
        base_id: str,
        field_id: str,
    ) -> Dict[str, Any]:
        """Alias for field_read_v3 (backwards compatibility).

        .. deprecated:: 3.0.0
            Use :meth:`field_read_v3` instead.
        """
        warnings.warn(
            "column_read_v3() is deprecated. Use field_read_v3() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.field_read_v3(base_id, field_id)

    def column_update_v3(
        self,
        base_id: str,
        field_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Alias for field_update_v3 (backwards compatibility).

        .. deprecated:: 3.0.0
            Use :meth:`field_update_v3` instead.
        """
        warnings.warn(
            "column_update_v3() is deprecated. Use field_update_v3() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.field_update_v3(base_id, field_id, body)

    def column_delete_v3(
        self,
        base_id: str,
        field_id: str,
    ) -> Dict[str, Any]:
        """Alias for field_delete_v3 (backwards compatibility).

        .. deprecated:: 3.0.0
            Use :meth:`field_delete_v3` instead.
        """
        warnings.warn(
            "column_delete_v3() is deprecated. Use field_delete_v3() instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self.field_delete_v3(base_id, field_id)

    # =========================================================================
    # v2 Meta API Methods - Views
    # =========================================================================

    def views_list(
        self,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all views for a table using v2 API.

        GET /api/v2/meta/tables/{tableId}/views

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            table_id: The table ID
            params: Optional query parameters

        Returns:
            Dict with 'list' array of views
            Example: {"list": [{"id": "vw_abc", "title": "Grid View", "type": 3}]}
        """
        url = self.__api_info.get_views_uri(table_id)
        return self._request("GET", url, params=params).json()

    def view_create(
        self,
        table_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new view for a table using v2 API.

        POST /api/v2/meta/tables/{tableId}/views

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        View types:
            - 3: grid
            - 1: gallery
            - 2: kanban
            - 4: calendar
            - 5: form

        Args:
            table_id: The table ID
            body: View configuration
                Example: {"title": "My View", "type": 3}

        Returns:
            Created view object with id, title, type, etc.
        """
        url = self.__api_info.get_views_uri(table_id)
        return self._request("POST", url, json=body).json()

    def view_read(
        self,
        view_id: str,
    ) -> Dict[str, Any]:
        """Read a single view's metadata using v2 API.

        GET /api/v2/meta/views/{viewId}

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID

        Returns:
            View object with id, title, type, etc.
        """
        url = self.__api_info.get_view_uri(view_id)
        return self._request("GET", url).json()

    def view_update(
        self,
        view_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a view's metadata using v2 API.

        PATCH /api/v2/meta/views/{viewId}

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID
            body: Fields to update (e.g., {"title": "NewName"})

        Returns:
            Updated view object
        """
        url = self.__api_info.get_view_uri(view_id)
        return self._request("PATCH", url, json=body).json()

    def view_delete(
        self,
        view_id: str,
    ) -> Dict[str, Any]:
        """Delete a view using v2 API.

        DELETE /api/v2/meta/views/{viewId}

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_view_uri(view_id)
        return self._request("DELETE", url).json()

    # =========================================================================
    # v2 Meta API Methods - View Sorts
    # =========================================================================

    def view_sorts_list(
        self,
        view_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all sorts for a view using v2 API.

        GET /api/v2/meta/views/{viewId}/sorts

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID
            params: Optional query parameters

        Returns:
            Dict with 'sorts' array
            Example: {"sorts": [{"id": "srt_abc", "fk_column_id": "fld_123", "direction": "asc"}]}
        """
        url = self.__api_info.get_view_sorts_uri(view_id)
        return self._request("GET", url, params=params).json()

    def view_sort_create(
        self,
        view_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new sort for a view using v2 API.

        POST /api/v2/meta/views/{viewId}/sorts

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID
            body: Sort configuration
                Example: {"fk_column_id": "fld_123", "direction": "asc"}

        Returns:
            Created sort object with id, fk_column_id, direction, etc.
        """
        url = self.__api_info.get_view_sorts_uri(view_id)
        return self._request("POST", url, json=body).json()

    def view_sort_update(
        self,
        sort_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a sort using v2 API.

        PATCH /api/v2/meta/sorts/{sortId}

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            sort_id: The sort ID
            body: Fields to update (e.g., {"direction": "desc"})

        Returns:
            Updated sort object
        """
        url = self.__api_info.get_sort_uri(sort_id)
        return self._request("PATCH", url, json=body).json()

    def view_sort_delete(
        self,
        sort_id: str,
    ) -> Dict[str, Any]:
        """Delete a sort using v2 API.

        DELETE /api/v2/meta/sorts/{sortId}

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            sort_id: The sort ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_sort_uri(sort_id)
        return self._request("DELETE", url).json()

    # =========================================================================
    # v2 Meta API Methods - View Filters
    # =========================================================================

    def view_filters_list(
        self,
        view_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all filters for a view using v2 API.

        GET /api/v2/meta/views/{viewId}/filters

        Note: v3 View Filters API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID
            params: Optional query parameters

        Returns:
            Dict with 'list' array of filters
            Example: {"list": [{"id": "flt_abc", "fk_column_id": "fld_123", "comparison_op": "eq", "value": "test"}]}
        """
        url = self.__api_info.get_view_filters_uri(view_id)
        return self._request("GET", url, params=params).json()

    def view_filter_create(
        self,
        view_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new filter for a view using v2 API.

        POST /api/v2/meta/views/{viewId}/filters

        Note: v3 View Filters API is Enterprise-only. Self-hosted NocoDB must use v2.

        Filter comparison operators:
            - eq, neq: Equal, Not equal
            - like, nlike: Like, Not like
            - gt, lt, gte, lte: Greater/Less than (or equal)
            - is, isnot: Is null, Is not null
            - empty, notempty: Is empty, Is not empty
            - in, notin: In array, Not in array

        Args:
            view_id: The view ID
            body: Filter configuration
                Example: {"fk_column_id": "fld_123", "comparison_op": "eq", "value": "test"}

        Returns:
            Created filter object with id, fk_column_id, comparison_op, value, etc.
        """
        url = self.__api_info.get_view_filters_uri(view_id)
        return self._request("POST", url, json=body).json()

    def view_filter_update(
        self,
        filter_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a filter using v2 API.

        PATCH /api/v2/meta/filters/{filterId}

        Note: v3 View Filters API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            filter_id: The filter ID
            body: Fields to update (e.g., {"comparison_op": "neq", "value": "updated"})

        Returns:
            Updated filter object
        """
        url = self.__api_info.get_filter_uri(filter_id)
        return self._request("PATCH", url, json=body).json()

    def view_filter_delete(
        self,
        filter_id: str,
    ) -> Dict[str, Any]:
        """Delete a filter using v2 API.

        DELETE /api/v2/meta/filters/{filterId}

        Note: v3 View Filters API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            filter_id: The filter ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_filter_uri(filter_id)
        return self._request("DELETE", url).json()

    # =========================================================================
    # v2 Meta API Methods - Webhooks
    # =========================================================================

    def webhooks_list(
        self,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all webhooks for a table using v2 API.

        GET /api/v2/meta/tables/{tableId}/hooks

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        Args:
            table_id: The table ID
            params: Optional query parameters

        Returns:
            Dict with 'list' array of webhooks
            Example: {"list": [{"id": "hk_abc", "title": "My Webhook", "event": "after.insert"}]}
        """
        url = self.__api_info.get_webhooks_uri(table_id)
        return self._request("GET", url, params=params).json()

    def webhook_create(
        self,
        table_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new webhook for a table using v2 API.

        POST /api/v2/meta/tables/{tableId}/hooks

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        Webhook events:
            - after.insert: After record insert
            - after.update: After record update
            - after.delete: After record delete
            - after.bulkInsert: After bulk insert
            - after.bulkUpdate: After bulk update
            - after.bulkDelete: After bulk delete

        Args:
            table_id: The table ID
            body: Webhook configuration
                Example: {
                    "title": "My Webhook",
                    "event": "after.insert",
                    "notification": {
                        "type": "URL",
                        "payload": {"method": "POST", "path": "https://example.com/hook"}
                    }
                }

        Returns:
            Created webhook object with id, title, event, etc.
        """
        url = self.__api_info.get_webhooks_uri(table_id)
        return self._request("POST", url, json=body).json()

    def webhook_read(
        self,
        hook_id: str,
    ) -> Dict[str, Any]:
        """Read a single webhook's metadata using v2 API.

        GET /api/v2/meta/hooks/{hookId}

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        Args:
            hook_id: The webhook (hook) ID

        Returns:
            Webhook object with id, title, event, notification, etc.
        """
        url = self.__api_info.get_webhook_uri(hook_id)
        return self._request("GET", url).json()

    def webhook_update(
        self,
        hook_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a webhook's configuration using v2 API.

        PATCH /api/v2/meta/hooks/{hookId}

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        Args:
            hook_id: The webhook (hook) ID
            body: Fields to update (e.g., {"title": "NewName", "active": false})

        Returns:
            Updated webhook object
        """
        url = self.__api_info.get_webhook_uri(hook_id)
        return self._request("PATCH", url, json=body).json()

    def webhook_delete(
        self,
        hook_id: str,
    ) -> Dict[str, Any]:
        """Delete a webhook using v2 API.

        DELETE /api/v2/meta/hooks/{hookId}

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        Args:
            hook_id: The webhook (hook) ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_webhook_uri(hook_id)
        return self._request("DELETE", url).json()

    def webhook_test(
        self,
        hook_id: str,
        body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Test a webhook using v2 API.

        POST /api/v2/meta/hooks/test/{hookId}

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        This endpoint triggers a test call to the webhook URL with sample payload.

        Args:
            hook_id: The webhook (hook) ID
            body: Optional test payload data

        Returns:
            Test result indicating success or failure
        """
        url = self.__api_info.get_webhook_test_uri(hook_id)
        return self._request("POST", url, json=body).json()

    # =========================================================================
    # v3 Meta API Methods - Base Members
    # =========================================================================

    def base_members_list(
        self,
        base_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List all members of a base.

        GET /api/v3/meta/bases/{baseId}/members

        Args:
            base_id: The base (project) ID
            params: Optional query parameters

        Returns:
            Dict with 'members' array
            Example: {"members": [{"id": "usr_abc", "email": "user@example.com", "roles": "editor"}]}
        """
        url = self.__api_info.get_base_members_uri(base_id)
        return self._request("GET", url, params=params).json()

    def base_member_add(
        self,
        base_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add a member to a base.

        POST /api/v3/meta/bases/{baseId}/members

        Args:
            base_id: The base (project) ID
            body: Member configuration with email and roles
                Example: {"email": "user@example.com", "roles": "editor"}
                Roles: owner, creator, editor, commenter, viewer

        Returns:
            Created member object
        """
        url = self.__api_info.get_base_members_uri(base_id)
        return self._request("POST", url, json=body).json()

    def base_member_update(
        self,
        base_id: str,
        member_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a base member's role.

        PATCH /api/v3/meta/bases/{baseId}/members/{memberId}

        Args:
            base_id: The base (project) ID
            member_id: The member ID
            body: Fields to update (e.g., {"roles": "viewer"})
                Roles: owner, creator, editor, commenter, viewer

        Returns:
            Updated member object
        """
        url = self.__api_info.get_base_member_uri(base_id, member_id)
        return self._request("PATCH", url, json=body).json()

    def base_member_remove(
        self,
        base_id: str,
        member_id: str,
    ) -> Dict[str, Any]:
        """Remove a member from a base.

        DELETE /api/v3/meta/bases/{baseId}/members/{memberId}

        Args:
            base_id: The base (project) ID
            member_id: The member ID

        Returns:
            Deletion confirmation
        """
        url = self.__api_info.get_base_member_uri(base_id, member_id)
        return self._request("DELETE", url).json()
