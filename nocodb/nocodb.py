"""
NocoDB Python Client - v3 API
SPDX-License-Identifier: AGPL-3.0-or-later

Copyright (C) 2026 Steve Goldberg

Based on nocodb-python-client by Samuel López Saura (MIT License, 2022)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
import warnings


class AuthToken(ABC):
    @abstractmethod
    def get_header(self) -> dict:
        pass


class APIToken(AuthToken):
    def __init__(self, token: str):
        self.__token = token

    def get_header(self) -> dict:
        return {"xc-token": self.__token}


class JWTAuthToken(AuthToken):
    def __init__(self, token: str):
        self.__token = token

    def get_header(self) -> dict:
        return {"xc-auth": self.__token}


class WhereFilter(ABC):
    @abstractmethod
    def get_where(self) -> str:
        pass


class NocoDBBase:
    """Represents a NocoDB base (formerly called project in v1 API).

    In the v3 API hierarchy: workspace -> base -> table
    The base_id is used in API paths like /api/v3/data/{baseId}/{tableId}/records

    Args:
        base_id: The base ID (e.g., "pgfqcp0ocloo1j3")
        workspace_id: Optional workspace ID, needed for some meta operations

    Example:
        >>> base = NocoDBBase("pgfqcp0ocloo1j3")
        >>> base = NocoDBBase("pgfqcp0ocloo1j3", workspace_id="ws_abc123")
    """

    def __init__(self, base_id: str, workspace_id: str = None):
        self._base_id = base_id
        self._workspace_id = workspace_id

    @property
    def base_id(self) -> str:
        """The base ID used in v3 API paths."""
        return self._base_id

    @property
    def workspace_id(self) -> str:
        """The workspace ID (optional, needed for some meta operations)."""
        return self._workspace_id

    # Deprecated property aliases for backwards compatibility
    @property
    def org_name(self) -> str:
        """Deprecated: Use workspace_id instead."""
        warnings.warn(
            "org_name is deprecated. Use workspace_id instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._workspace_id or ""

    @property
    def project_name(self) -> str:
        """Deprecated: Use base_id instead."""
        warnings.warn(
            "project_name is deprecated. Use base_id instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return self._base_id

    def __repr__(self) -> str:
        if self._workspace_id:
            return f"NocoDBBase(base_id={self._base_id!r}, workspace_id={self._workspace_id!r})"
        return f"NocoDBBase(base_id={self._base_id!r})"


class NocoDBProject(NocoDBBase):
    """Deprecated: Use NocoDBBase instead.

    This class is maintained for backwards compatibility with code written
    for the v1 API. New code should use NocoDBBase directly.

    .. deprecated:: 0.2.0
        Use :class:`NocoDBBase` instead.
    """

    def __init__(self, org_name: str = None, project_name: str = None, *, base_id: str = None, workspace_id: str = None):
        """Initialize a NocoDBProject (deprecated, use NocoDBBase).

        For backwards compatibility, accepts either:
        - Legacy style: NocoDBProject(org_name, project_name)
        - New style: NocoDBProject(base_id=..., workspace_id=...)

        Args:
            org_name: Deprecated. Maps to workspace_id.
            project_name: Deprecated. Maps to base_id.
            base_id: The base ID (preferred).
            workspace_id: The workspace ID (preferred).
        """
        warnings.warn(
            "NocoDBProject is deprecated. Use NocoDBBase instead.",
            DeprecationWarning,
            stacklevel=2
        )

        # Handle legacy positional arguments
        if base_id is None and project_name is not None:
            base_id = project_name
        if workspace_id is None and org_name is not None:
            workspace_id = org_name

        if base_id is None:
            raise ValueError("base_id (or project_name for legacy code) is required")

        super().__init__(base_id=base_id, workspace_id=workspace_id)


class NocoDBClient:
    @abstractmethod
    def table_row_list(
        self, project: NocoDBProject, table: str, filter_obj=None, params=None
    ) -> dict:
        pass

    @abstractmethod
    def table_row_list(
        self,
        project: NocoDBProject,
        table: str,
        filter_obj: Optional[WhereFilter] = None,
        params: Optional[dict] = None,
    ) -> dict:
        pass

    @abstractmethod
    def table_row_create(
        self, project: NocoDBProject, table: str, body: dict
    ) -> dict:
        pass

    @abstractmethod
    def table_row_detail(
        self, project: NocoDBProject, table: str, row_id: int
    ) -> dict:
        pass

    @abstractmethod
    def table_row_update(
        self, project: NocoDBProject, table: str, row_id: int, body: dict
    ) -> dict:
        pass

    @abstractmethod
    def table_row_delete(
        self, project: NocoDBProject, table: str, row_id: int
    ) -> int:
        pass

    @abstractmethod
    def table_row_nested_relations_list(
        self,
        project: NocoDBProject,
        table: str,
        relation_type: str,
        row_id: int,
        column_name: str,
    ) -> dict:
        """Deprecated: Use linked_records_list_v3() instead.

        .. deprecated:: 3.0.0
            This method uses the v1 API. Use :meth:`linked_records_list_v3` for v3 API.
        """
        pass

    @abstractmethod
    def table_create(
        self, project: NocoDBProject, body: dict
    ) -> dict:
        pass

    @abstractmethod
    def table_list(
        self,
        project: NocoDBProject,
        params: Optional[dict] = None,
    ) -> dict:
        pass

    @abstractmethod
    def table_read(
        self, tableId: str,
    ) -> dict:
        pass

    @abstractmethod
    def table_update(
        self, tableId: str, body: dict,
    ) -> bool:
        pass

    @abstractmethod
    def table_delete(
        self, tableId: str,
    ) -> dict:
        pass

    @abstractmethod
    def table_reorder(
        self, tableId: str, order: int,
    ) -> dict:
        pass

    @abstractmethod
    def table_column_create(
        self, tableId: str, body: dict,
    ) -> dict:
        pass

    @abstractmethod
    def table_column_update(
        self, columnId: str, body: dict,
    ) -> dict:
        pass

    @abstractmethod
    def table_column_delete(
        self, columnId: str,
    ) -> dict:
        pass

    @abstractmethod
    def table_column_set_primary(
        self, columnId: str,
    ) -> dict:
        pass

    # =========================================================================
    # v3 Data API Methods
    # =========================================================================

    @abstractmethod
    def records_list_v3(
        self,
        base_id: str,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List records using v3 API.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            params: Optional query parameters (fields, sort, where, page, pageSize, viewId)

        Returns:
            Dict with 'records' array and optional 'next' pagination URL
        """
        pass

    @abstractmethod
    def record_get_v3(
        self,
        base_id: str,
        table_id: str,
        record_id: Union[int, str],
    ) -> Dict[str, Any]:
        """Get a single record using v3 API.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            record_id: The record ID

        Returns:
            Dict with 'id' and 'fields'
        """
        pass

    @abstractmethod
    def records_create_v3(
        self,
        base_id: str,
        table_id: str,
        records: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Create one or more records using v3 API.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            records: Single record dict or list of record dicts with 'fields' key

        Returns:
            List of created records with 'id' and 'fields'
        """
        pass

    @abstractmethod
    def records_update_v3(
        self,
        base_id: str,
        table_id: str,
        records: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """Update one or more records using v3 API.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            records: Single record dict or list with 'id' and 'fields' keys

        Returns:
            List of updated records with 'id' and 'fields'
        """
        pass

    @abstractmethod
    def records_delete_v3(
        self,
        base_id: str,
        table_id: str,
        record_ids: Union[int, str, List[Union[int, str]]],
    ) -> List[Dict[str, Any]]:
        """Delete one or more records using v3 API.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            record_ids: Single record ID or list of record IDs

        Returns:
            List of deleted record IDs
        """
        pass

    @abstractmethod
    def records_count_v3(
        self,
        base_id: str,
        table_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, int]:
        """Get record count using v3 API.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            params: Optional query parameters (e.g., where filter)

        Returns:
            Dict with 'count' key
        """
        pass

    @abstractmethod
    def linked_records_list_v3(
        self,
        base_id: str,
        table_id: str,
        link_field_id: str,
        record_id: Union[int, str],
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List linked records for a specific record using v3 API.

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            link_field_id: The link field ID
            record_id: The record ID
            params: Optional query parameters (fields, sort, where, page, pageSize)

        Returns:
            Dict with 'list' array of linked records and optional 'next' pagination URL
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v3 Meta API Methods
    # =========================================================================

    @abstractmethod
    def workspaces_list_v3(
        self,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List workspaces using v3 API (Enterprise feature).

        Args:
            params: Optional query parameters

        Returns:
            Dict with 'workspaces' array
        """
        pass

    @abstractmethod
    def bases_list_v3(
        self,
        workspace_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List bases using v3 API.

        For self-hosted NocoDB (no workspaces):
            GET /api/v3/meta/bases

        For Enterprise/Cloud (with workspaces):
            GET /api/v3/meta/workspaces/{workspaceId}/bases

        Args:
            workspace_id: The workspace ID (optional, not needed for self-hosted)
            params: Optional query parameters

        Returns:
            Dict with 'bases' array
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def tables_list_v3(
        self,
        base_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List tables in a base using v3 API.

        Args:
            base_id: The base (project) ID
            params: Optional query parameters

        Returns:
            Dict with 'tables' array
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v3 Meta API Methods - Scripts
    # =========================================================================

    @abstractmethod
    def scripts_list_v3(
        self,
        base_id: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """List scripts in a base.

        GET /api/v3/meta/bases/{baseId}/scripts

        Args:
            base_id: The base (project) ID
            params: Optional query parameters

        Returns:
            Dict with scripts array
        """
        pass

    @abstractmethod
    def script_create_v3(
        self,
        base_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a new script.

        POST /api/v3/meta/bases/{baseId}/scripts

        Args:
            base_id: The base (project) ID
            body: Script configuration (title, script content, etc.)

        Returns:
            Created script object
        """
        pass

    @abstractmethod
    def script_read_v3(
        self,
        base_id: str,
        script_id: str,
    ) -> Dict[str, Any]:
        """Read a single script.

        GET /api/v3/meta/bases/{baseId}/scripts/{scriptId}

        Args:
            base_id: The base (project) ID
            script_id: The script ID

        Returns:
            Script object with details
        """
        pass

    @abstractmethod
    def script_update_v3(
        self,
        base_id: str,
        script_id: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update a script.

        PATCH /api/v3/meta/bases/{baseId}/scripts/{scriptId}

        Args:
            base_id: The base (project) ID
            script_id: The script ID
            body: Fields to update

        Returns:
            Updated script object
        """
        pass

    @abstractmethod
    def script_delete_v3(
        self,
        base_id: str,
        script_id: str,
    ) -> Dict[str, Any]:
        """Delete a script.

        DELETE /api/v3/meta/bases/{baseId}/scripts/{scriptId}

        Args:
            base_id: The base (project) ID
            script_id: The script ID

        Returns:
            Deletion confirmation
        """
        pass

    # =========================================================================
    # v3 Meta API Methods - API Tokens
    # =========================================================================

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v3 Meta API Methods - Fields
    # =========================================================================

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v2 Meta API Methods - Views
    # =========================================================================

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v2 Meta API Methods - View Sorts
    # =========================================================================

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v2 Meta API Methods - View Filters
    # =========================================================================

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v2 Meta API Methods - Webhooks
    # =========================================================================

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    # =========================================================================
    # v3 Meta API Methods - Base Members
    # =========================================================================

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
