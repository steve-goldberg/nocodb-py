from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
import warnings

"""
License MIT

Copyright 2022 Samuel López Saura

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


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
