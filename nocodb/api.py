import warnings
from enum import Enum
from typing import Optional
from urllib.parse import urljoin
from .nocodb import NocoDBBase, NocoDBProject


class NocoDBAPIUris(Enum):
    """NocoDB API URI prefixes.

    v3 API uses baseId/tableId in paths instead of org/project/table.
    v2 API is required for some features (bases list) in self-hosted NocoDB.
    """
    # Legacy v1 prefixes (deprecated)
    V1_DB_DATA_PREFIX = "api/v1/db/data/"
    V1_DB_META_PREFIX = "api/v1/db/meta/"

    # v2 API prefixes (needed for self-hosted features)
    V2_META_PREFIX = "api/v2/meta/"

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
        # Store the raw base URI for download URLs
        self.__raw_base_uri = base_uri.rstrip("/")

        # v3 API base URIs
        self.__base_data_uri = urljoin(base_uri + "/", NocoDBAPIUris.V3_DATA_PREFIX.value)
        self.__base_meta_uri = urljoin(base_uri + "/", NocoDBAPIUris.V3_META_PREFIX.value)

        # v2 API base URIs (for self-hosted features like bases list)
        self.__base_meta_uri_v2 = urljoin(base_uri + "/", NocoDBAPIUris.V2_META_PREFIX.value)

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

    def get_attachment_upload_uri(
        self,
        base_id: str,
        table_id: str,
        record_id: str,
        field_id: str
    ) -> str:
        """Get the URI for uploading attachments to a record field.

        v3 endpoint: POST /api/v3/data/{baseId}/{tableId}/records/{recordId}/fields/{fieldId}/upload

        Args:
            base_id: The base (project) ID
            table_id: The table ID
            record_id: The record ID
            field_id: The attachment field ID

        Returns:
            The URI for attachment upload
        """
        return urljoin(
            self.__base_data_uri,
            "/".join((base_id, table_id, "records", str(record_id), "fields", field_id, "upload"))
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
    # v2 Meta API URI Methods (for self-hosted NocoDB)
    # =========================================================================

    def get_bases_list_uri_v2(self) -> str:
        """Get the URI for listing bases using v2 API.

        v2 endpoint: GET /api/v2/meta/bases

        Note: v3 bases list is Enterprise-only. Self-hosted NocoDB must use v2.

        Returns:
            The URI for bases list
        """
        return urljoin(self.__base_meta_uri_v2, "bases")

    def get_base_create_uri_v2(self) -> str:
        """Get the URI for creating a base using v2 API.

        v2 endpoint: POST /api/v2/meta/bases

        Note: v3 base creation is Enterprise-only. Self-hosted NocoDB must use v2.

        Returns:
            The URI for base creation
        """
        return urljoin(self.__base_meta_uri_v2, "bases")

    def get_views_uri(self, table_id: str) -> str:
        """Get the URI for listing/creating views using v2 API.

        v2 endpoint: GET/POST /api/v2/meta/tables/{tableId}/views

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            table_id: The table ID

        Returns:
            The URI for views list/create operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("tables", table_id, "views")))

    def get_view_uri(self, view_id: str) -> str:
        """Get the URI for single view operations using v2 API.

        v2 endpoint: GET/PATCH/DELETE /api/v2/meta/views/{viewId}

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID

        Returns:
            The URI for single view operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id)))

    def get_view_sorts_uri(self, view_id: str) -> str:
        """Get the URI for listing/creating view sorts using v2 API.

        v2 endpoint: GET/POST /api/v2/meta/views/{viewId}/sorts

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID

        Returns:
            The URI for view sorts list/create operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id, "sorts")))

    def get_sort_uri(self, sort_id: str) -> str:
        """Get the URI for single sort operations using v2 API.

        v2 endpoint: PATCH/DELETE /api/v2/meta/sorts/{sortId}

        Note: v3 Views API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            sort_id: The sort ID

        Returns:
            The URI for single sort operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("sorts", sort_id)))

    def get_view_filters_uri(self, view_id: str) -> str:
        """Get the URI for view filters operations using v2 API.

        v2 endpoint: GET/POST /api/v2/meta/views/{viewId}/filters

        Note: v3 View Filters API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            view_id: The view ID

        Returns:
            The URI for view filters list/create operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id, "filters")))

    def get_filter_uri(self, filter_id: str) -> str:
        """Get the URI for single filter operations using v2 API.

        v2 endpoint: PATCH/DELETE /api/v2/meta/filters/{filterId}

        Note: v3 View Filters API is Enterprise-only. Self-hosted NocoDB must use v2.

        Args:
            filter_id: The filter ID

        Returns:
            The URI for single filter operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("filters", filter_id)))

    def get_webhooks_uri(self, table_id: str) -> str:
        """Get the URI for listing/creating webhooks using v2 API.

        v2 endpoint: GET/POST /api/v2/meta/tables/{tableId}/hooks

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        Args:
            table_id: The table ID

        Returns:
            The URI for webhooks list/create operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("tables", table_id, "hooks")))

    def get_webhook_uri(self, hook_id: str) -> str:
        """Get the URI for single webhook operations using v2 API.

        v2 endpoint: GET/PATCH/DELETE /api/v2/meta/hooks/{hookId}

        Note: Webhooks haven't migrated to v3 yet. Use v2 API.

        Args:
            hook_id: The webhook (hook) ID

        Returns:
            The URI for single webhook operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("hooks", hook_id)))

    # Note: get_webhook_test_uri removed - webhook_test not supported in self-hosted NocoDB

    # =========================================================================
    # v2 Export API URI Methods
    # =========================================================================

    def get_export_uri(self, view_id: str) -> str:
        """Get the URI for exporting view data to CSV.

        v2 endpoint: POST /api/v2/export/{viewId}/csv

        Note: Only CSV format is supported in self-hosted NocoDB.

        Args:
            view_id: The view ID

        Returns:
            The URI for export operation
        """
        # Export uses a different base path: /api/v2/export/
        base_uri = self.__base_meta_uri_v2.replace("/meta/", "/export/")
        return base_uri + view_id + "/csv"

    def get_jobs_uri(self, base_id: str) -> str:
        """Get the URI for job status polling.

        v2 endpoint: POST /api/v2/jobs/{baseId}

        Args:
            base_id: The base ID

        Returns:
            The URI for job status operations
        """
        # Jobs uses a different base path: /api/v2/jobs/
        base_uri = self.__base_meta_uri_v2.replace("/meta/", "/jobs/")
        return base_uri + base_id

    def get_download_uri(self, relative_path: str) -> str:
        """Get the full download URI for a relative path.

        Args:
            relative_path: The relative path from job result (e.g., "dltemp/...")

        Returns:
            The full download URL
        """
        return f"{self.__raw_base_uri}/{relative_path}"

    # =========================================================================
    # v2 View Columns API URI Methods
    # =========================================================================

    def get_view_columns_uri(self, view_id: str) -> str:
        """Get the URI for listing/creating view columns.

        v2 endpoint: GET/POST /api/v2/meta/views/{viewId}/columns

        Args:
            view_id: The view ID

        Returns:
            The URI for view columns list/create operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id, "columns")))

    def get_view_column_uri(self, view_id: str, column_id: str) -> str:
        """Get the URI for single view column operations.

        v2 endpoint: PATCH /api/v2/meta/views/{viewId}/columns/{columnId}

        Args:
            view_id: The view ID
            column_id: The column ID

        Returns:
            The URI for single view column operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id, "columns", column_id)))

    def get_view_hide_all_uri(self, view_id: str) -> str:
        """Get the URI for hiding all columns in a view.

        v2 endpoint: POST /api/v2/meta/views/{viewId}/hide-all

        Args:
            view_id: The view ID

        Returns:
            The URI for hide-all operation
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id, "hide-all")))

    def get_view_show_all_uri(self, view_id: str) -> str:
        """Get the URI for showing all columns in a view.

        v2 endpoint: POST /api/v2/meta/views/{viewId}/show-all

        Args:
            view_id: The view ID

        Returns:
            The URI for show-all operation
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id, "show-all")))

    # =========================================================================
    # v2 Shared Views API URI Methods
    # =========================================================================

    def get_shared_views_uri(self, table_id: str) -> str:
        """Get the URI for listing shared views for a table.

        v2 endpoint: GET /api/v2/meta/tables/{tableId}/share

        Args:
            table_id: The table ID

        Returns:
            The URI for shared views list
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("tables", table_id, "share")))

    def get_shared_view_uri(self, view_id: str) -> str:
        """Get the URI for shared view operations.

        v2 endpoint: POST/PATCH/DELETE /api/v2/meta/views/{viewId}/share

        Args:
            view_id: The view ID

        Returns:
            The URI for shared view operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("views", view_id, "share")))

    # =========================================================================
    # v2 Storage API URI Methods
    # =========================================================================

    def get_storage_upload_uri(self) -> str:
        """Get the URI for uploading files to storage.

        v2 endpoint: POST /api/v2/storage/upload

        Note: This is for general file upload, not record-attached attachments.

        Returns:
            The URI for storage upload
        """
        # Storage uses a different base path: /api/v2/storage/
        base_uri = self.__base_meta_uri_v2.replace("/meta/", "/storage/")
        return base_uri + "upload"

    # =========================================================================
    # v2 Filter/Sort Metadata API URI Methods
    # =========================================================================

    def get_filter_children_uri(self, filter_group_id: str) -> str:
        """Get the URI for listing filter group children.

        v2 endpoint: GET /api/v2/meta/filters/{filterGroupId}/children

        Args:
            filter_group_id: The filter group ID

        Returns:
            The URI for filter children list
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("filters", filter_group_id, "children")))

    # =========================================================================
    # v2 Webhook Filters/Logs API URI Methods
    # =========================================================================

    def get_webhook_filters_uri(self, hook_id: str) -> str:
        """Get the URI for listing/creating webhook filters.

        v2 endpoint: GET/POST /api/v2/meta/hooks/{hookId}/filters

        Args:
            hook_id: The webhook (hook) ID

        Returns:
            The URI for webhook filters list/create operations
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("hooks", hook_id, "filters")))

    def get_webhook_logs_uri(self, hook_id: str) -> str:
        """Get the URI for listing webhook logs.

        v2 endpoint: GET /api/v2/meta/hooks/{hookId}/logs

        Args:
            hook_id: The webhook (hook) ID

        Returns:
            The URI for webhook logs list
        """
        return urljoin(self.__base_meta_uri_v2, "/".join(("hooks", hook_id, "logs")))

    def get_webhook_sample_payload_uri(self, table_id: str, event: str, operation: str, version: str = "v2") -> str:
        """Get the URI for webhook sample payload.

        v2 endpoint: GET /api/v2/meta/tables/{tableId}/hooks/samplePayload/{event}/{operation}/{version}

        Args:
            table_id: The table ID
            event: The event type (e.g., "records")
            operation: The operation (e.g., "insert", "update", "delete")
            version: The payload version (default: "v2")

        Returns:
            The URI for webhook sample payload
        """
        return urljoin(self.__base_meta_uri_v2, "/".join((
            "tables", table_id, "hooks", "samplePayload", event, operation, version
        )))

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
    # v3 Meta API URI Methods - Scripts
    # =========================================================================

    def get_scripts_uri(self, base_id: str) -> str:
        """Get the URI for scripts list/create operations.

        v3 endpoint: GET/POST /api/v3/meta/bases/{baseId}/scripts

        Args:
            base_id: The base (project) ID

        Returns:
            The URI for scripts list/create operations
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "scripts")))

    def get_script_uri(self, base_id: str, script_id: str) -> str:
        """Get the URI for single script operations.

        v3 endpoint: GET/PATCH/DELETE /api/v3/meta/bases/{baseId}/scripts/{scriptId}

        Args:
            base_id: The base (project) ID
            script_id: The script ID

        Returns:
            The URI for single script operations
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "scripts", script_id)))

    # =========================================================================
    # v3 Meta API URI Methods - Base Members
    # =========================================================================

    def get_base_members_uri(self, base_id: str) -> str:
        """Get the URI for listing/adding base members.

        v3 endpoint: GET/POST /api/v3/meta/bases/{baseId}/members

        Args:
            base_id: The base (project) ID

        Returns:
            The URI for base members list/create operations
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "members")))

    def get_base_member_uri(self, base_id: str, member_id: str) -> str:
        """Get the URI for single base member operations.

        v3 endpoint: PATCH/DELETE /api/v3/meta/bases/{baseId}/members/{memberId}

        Args:
            base_id: The base (project) ID
            member_id: The member ID

        Returns:
            The URI for single base member operations
        """
        return urljoin(self.__base_meta_uri, "/".join(("bases", base_id, "members", member_id)))

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
