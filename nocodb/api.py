import warnings
from enum import Enum
from typing import Optional
from urllib.parse import urljoin
from .nocodb import NocoDBBase, NocoDBProject


class NocoDBAPIUris(Enum):
    """NocoDB API URI prefixes.

    v3 API uses baseId/tableId in paths instead of org/project/table.
    """
    # Legacy v1 prefixes (deprecated)
    V1_DB_DATA_PREFIX = "api/v1/db/data/"
    V1_DB_META_PREFIX = "api/v1/db/meta/"

    # v3 API prefixes
    V3_DATA_PREFIX = "api/v3/data/"
    V3_META_PREFIX = "api/v3/meta/"


class NocoDBAPI:
    """NocoDB API URI builder.

    Builds URIs for the NocoDB v3 API. The v3 API uses baseId and tableId
    in paths instead of org/project/table structure.
    """

    def __init__(self, base_uri: str):
        """Initialize the API URI builder.

        Args:
            base_uri: The base URL of the NocoDB instance (e.g., "https://app.nocodb.com")
        """
        # v3 API base URIs
        self.__base_data_uri = urljoin(base_uri + "/", NocoDBAPIUris.V3_DATA_PREFIX.value)
        self.__base_meta_uri = urljoin(base_uri + "/", NocoDBAPIUris.V3_META_PREFIX.value)

        # Legacy v1 API base URIs (for backwards compatibility)
        self.__base_data_uri_v1 = urljoin(base_uri + "/", NocoDBAPIUris.V1_DB_DATA_PREFIX.value)
        self.__base_meta_uri_v1 = urljoin(base_uri + "/", NocoDBAPIUris.V1_DB_META_PREFIX.value)

    # =========================================================================
    # v3 Data API URI Methods
    # =========================================================================

    def get_records_uri(self, base_id: str, table_id: str) -> str:
        """Get the URI for listing/creating records.

        v3 endpoint: GET/POST /api/v3/data/{baseId}/{tableId}/records

        Args:
            base_id: The base (project) ID
            table_id: The table ID

        Returns:
            The URI for records operations
        """
        return urljoin(self.__base_data_uri, "/".join((base_id, table_id, "records")))

    def get_record_uri(self, base_id: str, table_id: str, record_id: str) -> str:
        """Get the URI for a specific record.

        v3 endpoint: GET/PATCH/DELETE /api/v3/data/{baseId}/{tableId}/records/{recordId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            record_id: The record ID

        Returns:
            The URI for single record operations
        """
        return urljoin(self.__base_data_uri, "/".join((base_id, table_id, "records", str(record_id))))

    def get_records_count_uri(self, base_id: str, table_id: str) -> str:
        """Get the URI for counting records.

        v3 endpoint: GET /api/v3/data/{baseId}/{tableId}/count

        Args:
            base_id: The base (project) ID
            table_id: The table ID

        Returns:
            The URI for count operation
        """
        return urljoin(self.__base_data_uri, "/".join((base_id, table_id, "count")))

    def get_linked_records_uri(
        self,
        base_id: str,
        table_id: str,
        link_field_id: str,
        record_id: str
    ) -> str:
        """Get the URI for linked records.

        v3 endpoint: GET /api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            link_field_id: The link field ID
            record_id: The record ID

        Returns:
            The URI for linked records operations
        """
        return urljoin(
            self.__base_data_uri,
            "/".join((base_id, table_id, "links", link_field_id, str(record_id)))
        )

    # =========================================================================
    # v3 Meta API URI Methods - Workspaces & Bases
    # =========================================================================

    def get_workspaces_uri(self) -> str:
        """Get the URI for listing workspaces.

        v3 endpoint: GET /api/v3/meta/workspaces

        Returns:
            The URI for workspaces list
        """
        return urljoin(self.__base_meta_uri, "workspaces")

    def get_bases_uri(self, workspace_id: str = None) -> str:
        """Get the URI for listing bases.

        v3 endpoints:
        - With workspace: GET /api/v3/meta/workspaces/{workspaceId}/bases
        - Without workspace (self-hosted): GET /api/v3/meta/bases

        Args:
            workspace_id: The workspace ID (optional for self-hosted without Enterprise)

        Returns:
            The URI for bases list
        """
        if workspace_id:
            return urljoin(self.__base_meta_uri, "/".join(("workspaces", workspace_id, "bases")))
        else:
            # Self-hosted NocoDB without workspaces
            return urljoin(self.__base_meta_uri, "bases")

    def get_base_uri(self, base_id: str) -> str:
        """Get the URI for a specific base.

        v3 endpoint: GET /api/v3/meta/bases/{baseId}

        Args:
            base_id: The base (project) ID

        Returns:
            The URI for base operations
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id)))

    # =========================================================================
    # v3 Meta API URI Methods - Tables
    # =========================================================================

    def get_tables_uri(self, base_id: str) -> str:
        """Get the URI for listing tables in a base.

        v3 endpoint: GET /api/v3/meta/bases/{baseId}/tables

        Args:
            base_id: The base (project) ID

        Returns:
            The URI for tables list
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "tables")))

    def get_table_meta_uri_v3(self, base_id: str, table_id: str) -> str:
        """Get the URI for table metadata.

        v3 endpoint: GET /api/v3/meta/bases/{baseId}/tables/{tableId}

        Args:
            base_id: The base (project) ID
            table_id: The table ID

        Returns:
            The URI for table metadata
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "tables", table_id)))

    # =========================================================================
    # v3 Meta API URI Methods - Fields
    # =========================================================================

    def get_fields_uri(self, base_id: str, table_id: str) -> str:
        """Get the URI for listing/creating fields in a table.

        v3 endpoint: POST /api/v3/meta/bases/{baseId}/tables/{tableId}/fields

        Args:
            base_id: The base (project) ID
            table_id: The table ID

        Returns:
            The URI for fields operations
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "tables", table_id, "fields")))

    def get_field_uri(self, base_id: str, field_id: str) -> str:
        """Get the URI for a specific field.

        v3 endpoint: GET /api/v3/meta/bases/{baseId}/fields/{fieldId}

        Args:
            base_id: The base (project) ID
            field_id: The field ID

        Returns:
            The URI for field operations
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "fields", field_id)))

    # =========================================================================
    # Deprecated v1 API Methods - Backwards Compatibility
    # =========================================================================

    def get_table_uri(self, project: NocoDBProject, table: str) -> str:
        """Get the URI for table data operations (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_records_uri` with base_id and table_id instead.

        Args:
            project: The NocoDB project
            table: The table name

        Returns:
            The URI for table data operations
        """
        warnings.warn(
            "get_table_uri() is deprecated. Use get_records_uri(base_id, table_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return urljoin(self.__base_data_uri_v1, "/".join(
            (
                project.org_name,
                project.project_name,
                table,
            )
        ))

    def get_table_count_uri(self, project: NocoDBProject, table: str) -> str:
        """Get the URI for counting table rows (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_records_count_uri` with base_id and table_id instead.

        Args:
            project: The NocoDB project
            table: The table name

        Returns:
            The URI for count operation
        """
        warnings.warn(
            "get_table_count_uri() is deprecated. Use get_records_count_uri(base_id, table_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return "/".join(
            (
                self.get_table_uri.__wrapped__(self, project, table) if hasattr(self.get_table_uri, '__wrapped__')
                else urljoin(self.__base_data_uri_v1, "/".join((project.org_name, project.project_name, table))),
                'count'
            )
        )

    def get_table_find_one_uri(self, project: NocoDBProject, table: str) -> str:
        """Get the URI for finding one row (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_records_uri` with query parameters instead.

        Args:
            project: The NocoDB project
            table: The table name

        Returns:
            The URI for find-one operation
        """
        warnings.warn(
            "get_table_find_one_uri() is deprecated. Use get_records_uri(base_id, table_id) with limit=1 instead.",
            DeprecationWarning,
            stacklevel=2
        )
        base_uri = urljoin(self.__base_data_uri_v1, "/".join((project.org_name, project.project_name, table)))
        return "/".join((base_uri, 'find-one'))

    def get_row_detail_uri(
        self, project: NocoDBProject, table: str, row_id: int
    ) -> str:
        """Get the URI for row detail operations (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_record_uri` with base_id, table_id, and record_id instead.

        Args:
            project: The NocoDB project
            table: The table name
            row_id: The row ID

        Returns:
            The URI for row detail operations
        """
        warnings.warn(
            "get_row_detail_uri() is deprecated. Use get_record_uri(base_id, table_id, record_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return urljoin(self.__base_data_uri_v1, "/".join(
            (
                project.org_name,
                project.project_name,
                table,
                str(row_id),
            )
        ))

    def get_nested_relations_rows_list_uri(
        self,
        project: NocoDBProject,
        table: str,
        relation_type: str,
        row_id: int,
        column_name: str,
    ) -> str:
        """Get the URI for nested relations (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_linked_records_uri` with base_id, table_id, link_field_id, and record_id instead.

        Args:
            project: The NocoDB project
            table: The table name
            relation_type: The relation type (mm, hm, bt)
            row_id: The row ID
            column_name: The column name

        Returns:
            The URI for nested relations operations
        """
        warnings.warn(
            "get_nested_relations_rows_list_uri() is deprecated. Use get_linked_records_uri(base_id, table_id, link_field_id, record_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return urljoin(self.__base_data_uri_v1, "/".join(
            (
                project.org_name,
                project.project_name,
                table,
                str(row_id),
                relation_type,
                column_name,
            )
        ))

    def get_project_uri(self) -> str:
        """Get the URI for project operations (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_bases_uri` with workspace_id instead.

        Returns:
            The URI for project operations
        """
        warnings.warn(
            "get_project_uri() is deprecated. Use get_bases_uri(workspace_id) or get_base_uri(base_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return urljoin(self.__base_meta_uri_v1, "projects")

    def get_project_tables_uri(self, project: NocoDBProject) -> str:
        """Get the URI for project tables (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_tables_uri` with base_id instead.

        Args:
            project: The NocoDB project

        Returns:
            The URI for project tables
        """
        warnings.warn(
            "get_project_tables_uri() is deprecated. Use get_tables_uri(base_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return urljoin(self.__base_meta_uri_v1, "/".join(
            (
                "projects",
                project.project_name,
                "tables"
            )
        ))

    def get_table_meta_uri(
        self, tableId: str, operation: Optional[str] = None,
    ) -> str:
        """Get the URI for table metadata operations (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_table_meta_uri_v3` with base_id and table_id instead.

        Args:
            tableId: The table ID
            operation: Optional operation path segment

        Returns:
            The URI for table metadata operations
        """
        warnings.warn(
            "get_table_meta_uri() is deprecated. Use get_table_meta_uri_v3(base_id, table_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        additional_path = []
        if operation is not None:
            additional_path.append(operation)

        return urljoin(self.__base_meta_uri_v1, "/".join(
            [
                "tables",
                tableId,
            ] + additional_path
        ))

    def get_column_uri(
        self, columnId: str, operation: Optional[str] = None,
    ) -> str:
        """Get the URI for column operations (DEPRECATED).

        .. deprecated:: 0.2.0
            Use :meth:`get_field_uri` with base_id and field_id instead.

        Args:
            columnId: The column ID
            operation: Optional operation path segment

        Returns:
            The URI for column operations
        """
        warnings.warn(
            "get_column_uri() is deprecated. Use get_field_uri(base_id, field_id) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        additional_path = []
        if operation is not None:
            additional_path.append(operation)

        return urljoin(self.__base_meta_uri_v1, "/".join(
            [
                "columns",
                columnId,
            ] + additional_path
        ))
