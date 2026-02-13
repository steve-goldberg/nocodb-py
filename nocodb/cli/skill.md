---
name: "nocodb-cli"
description: "CLI for the NocoDB MCP server. Call tools, list resources, and get prompts."
---

# NocoDB CLI

## Tool Commands

### records_list

List records from a table with optional filtering and pagination.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    fields: Comma-separated field names to include (e.g., "Name,Email,Status")
    sort: Sort field(s), prefix with - for descending (e.g., "-CreatedAt" or "Name,-Age")
    where: Filter condition using NocoDB syntax (e.g., "(Status,eq,Active)")
    page: Page number (1-indexed, default: 1)
    page_size: Records per page (default: 25, max: 1000)
    view_id: Optional view ID to filter by

Returns:
    RecordsListResult with records array and pagination info.

Filter syntax examples:
    - Equal: (Status,eq,Active)
    - Not equal: (Status,neq,Deleted)
    - Like: (Name,like,%john%)
    - Greater than: (Age,gt,18)
    - Is null: (Email,is,null)
    - Multiple: (Status,eq,Active)~and(Priority,eq,High)

```bash
nocodb call-tool records_list --table-id <value> --fields <value> --sort <value> --where <value> --page <value> --page-size <value> --view-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--fields` | string | no | JSON string |
| `--sort` | string | no | JSON string |
| `--where` | string | no | JSON string |
| `--page` | integer | no |  |
| `--page-size` | integer | no |  |
| `--view-id` | string | no | JSON string |

### records_list_all

Fetch all records from a table, automatically handling pagination.

Use with caution on large tables. Consider using records_list with
pagination for better control.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    where: Optional filter condition
    page_size: Records per page (default: 100)
    max_pages: Maximum pages to fetch (None = unlimited)

Returns:
    List of all matching records.

```bash
nocodb call-tool records_list_all --table-id <value> --where <value> --page-size <value> --max-pages <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--where` | string | no | JSON string |
| `--page-size` | integer | no |  |
| `--max-pages` | string | no | JSON string |

### record_get

Get a single record by ID.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    record_id: The record ID (e.g., "1" or "rec_xxx")

Returns:
    RecordResult with id and fields.

```bash
nocodb call-tool record_get --table-id <value> --record-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--record-id` | string | yes |  |

### records_create

Create one or more records in a table.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    records: List of record data dicts. Each dict should contain field values.
        Example: [{"Name": "John", "Email": "john@example.com"}]
        For batch: [{"Name": "A"}, {"Name": "B"}, {"Name": "C"}]

Returns:
    RecordsMutationResult with created records.

```bash
nocodb call-tool records_create --table-id <value> --records <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--records` | array[object] | yes | JSON string |

### records_update

Update one or more records in a table.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    records: List of record updates. Each dict must have "id" and field values.
        Example: [{"id": 1, "Status": "Done"}]
        For batch: [{"id": 1, "Status": "A"}, {"id": 2, "Status": "B"}]

Returns:
    RecordsMutationResult with updated records.

```bash
nocodb call-tool records_update --table-id <value> --records <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--records` | array[object] | yes | JSON string |

### records_delete

Delete one or more records from a table.

DESTRUCTIVE: This operation cannot be undone. Set confirm=True to proceed.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    record_ids: List of record IDs to delete (e.g., ["1", "2", "3"])
    confirm: Must be True to proceed with deletion

Returns:
    RecordsMutationResult with deleted record IDs.

```bash
nocodb call-tool records_delete --table-id <value> --record-ids <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--record-ids` | array[string] | yes |  |
| `--confirm` | boolean | no |  |

### records_count

Count records in a table, optionally filtered.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    where: Optional filter condition (e.g., "(Status,eq,Active)")

Returns:
    RecordsCountResult with count.

```bash
nocodb call-tool records_count --table-id <value> --where <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--where` | string | no | JSON string |

### bases_list

List all bases available to the current user.

Use this to discover base IDs for configuration.

Returns:
    BasesListResult with list of bases including id and title.

Note: The MCP server requires NOCODB_BASE_ID to be set.
This tool helps you find available base IDs if you need
to configure a different base.

```bash
nocodb call-tool bases_list
```

### base_info

Get detailed information about the currently configured base.

Returns the base metadata including title and list of tables.

Returns:
    BaseInfoResult with base id, title, tables, and metadata.

```bash
nocodb call-tool base_info
```

### tables_list

List all tables in the current base.

Returns:
    TablesListResult with list of tables including id, title, and type.

```bash
nocodb call-tool tables_list
```

### table_get

Get detailed information about a table including its fields.

Args:
    table_id: The table ID (e.g., "tbl_xxx")

Returns:
    TableResult with id, title, fields, and metadata.

```bash
nocodb call-tool table_get --table-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |

### table_create

Create a new table in the current base.

Args:
    title: The table title (e.g., "Users", "Tasks")
    fields: Optional list of field definitions to create with the table.
        Each field should have "title" and "type" keys.
        Example: [{"title": "Name", "type": "SingleLineText"}, {"title": "Email", "type": "Email"}]

Returns:
    TableResult with created table details.

Field types:
    - SingleLineText: Short text
    - LongText: Multi-line text
    - Number: Integer
    - Decimal: Float (options: {"precision": 2})
    - Email: Email address
    - URL: Web link
    - PhoneNumber: Phone
    - Date: Date only
    - DateTime: Date + time
    - Checkbox: Boolean
    - SingleSelect: Dropdown (options: {"options": {"choices": [{"title": "A"}]}})
    - MultiSelect: Multi-dropdown
    - Rating: Star rating
    - Attachment: File upload
    - Links: Relationship to another table

```bash
nocodb call-tool table_create --title <value> --fields <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--title` | string | yes |  |
| `--fields` | string | no | JSON string |

### table_update

Update a table's metadata.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    title: New table title
    icon: Table icon (emoji, e.g., "🎯")
    meta: Additional metadata dict

Returns:
    TableResult with updated table details.

```bash
nocodb call-tool table_update --table-id <value> --title <value> --icon <value> --meta <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--title` | string | no | JSON string |
| `--icon` | string | no | JSON string |
| `--meta` | string | no | JSON string |

### table_delete

Delete a table and all its data.

DESTRUCTIVE: This permanently deletes the table, all its fields,
and ALL RECORDS. This cannot be undone. Set confirm=True to proceed.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    confirm: Must be True to proceed with deletion

Returns:
    TableDeleteResult with success status.

```bash
nocodb call-tool table_delete --table-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### fields_list

List all fields in a table.

Args:
    table_id: The table ID (e.g., "tbl_xxx")

Returns:
    FieldsListResult with list of fields including id, title, type, and options.

```bash
nocodb call-tool fields_list --table-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |

### field_get

Get detailed information about a field.

Args:
    field_id: The field ID (e.g., "fld_xxx")

Returns:
    FieldResult with id, title, type, and options.

```bash
nocodb call-tool field_get --field-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--field-id` | string | yes |  |

### field_create

Create a new field in a table.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    title: The field title (e.g., "Status", "Email")
    field_type: The field type (see list below)
    options: Optional field-specific options

Returns:
    FieldResult with created field details.

Field types:
    - SingleLineText: Short text
    - LongText: Multi-line text
    - Number: Integer
    - Decimal: Float (options: {"precision": 2})
    - Currency: Money (options: {"locale": "en-US", "code": "USD"})
    - Percent: Percentage
    - Email: Email address
    - URL: Web link
    - PhoneNumber: Phone
    - Date: Date only (options: {"date_format": "YYYY-MM-DD"})
    - DateTime: Date + time
    - Time: Time only
    - Duration: Time span
    - Checkbox: Boolean
    - SingleSelect: Dropdown
        options: {"options": {"choices": [{"title": "A", "color": "#00FF00"}]}}
    - MultiSelect: Multi-dropdown (same options as SingleSelect)
    - Rating: Star rating (options: {"max": 5})
    - Attachment: File upload
    - Links: Relationship
        options: {"relation_type": "hm", "related_table_id": "tbl_xxx"}
        relation_type: "hm" (has many), "bt" (belongs to), "mm" (many to many)
    - Lookup: Related field value
    - Rollup: Aggregation of related records
    - Formula: Calculated field (options: {"formula": "..."})

SingleSelect/MultiSelect colors: Use HEX codes like "#00FF00", not color names.

```bash
nocodb call-tool field_create --table-id <value> --title <value> --field-type <value> --options <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--title` | string | yes |  |
| `--field-type` | string | yes |  |
| `--options` | string | no | JSON string |

### field_update

Update a field's metadata.

Note: For updating SingleSelect/MultiSelect colors, use field_update_options instead.

Args:
    field_id: The field ID (e.g., "fld_xxx")
    title: New field title
    options: New field options (not for colOptions updates)

Returns:
    FieldResult with updated field details.

```bash
nocodb call-tool field_update --field-id <value> --title <value> --options <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--field-id` | string | yes |  |
| `--title` | string | no | JSON string |
| `--options` | string | no | JSON string |

### field_update_options

Update a field's colOptions using v2 API.

Use this specifically for updating SingleSelect/MultiSelect choice colors,
which requires the v2 column update API.

Args:
    field_id: The field ID (e.g., "fld_xxx")
    col_options: The colOptions dict with updated choices.
        Example for SingleSelect colors:
        {
            "options": [
                {"id": "opt_xxx", "title": "Active", "color": "#00FF00"},
                {"id": "opt_yyy", "title": "Inactive", "color": "#FF0000"}
            ]
        }

Returns:
    FieldResult with updated field details.

Note: You must include the option "id" for existing options.
Get the current option IDs using field_get first.

```bash
nocodb call-tool field_update_options --field-id <value> --col-options <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--field-id` | string | yes |  |
| `--col-options` | object | yes | JSON string |

### field_delete

Delete a field from a table.

DESTRUCTIVE: This permanently deletes the field and ALL DATA in that field
across all records. This cannot be undone. Set confirm=True to proceed.

Args:
    field_id: The field ID (e.g., "fld_xxx")
    confirm: Must be True to proceed with deletion

Returns:
    FieldDeleteResult with success status.

```bash
nocodb call-tool field_delete --field-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--field-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### linked_records_list

List records linked to a specific record via a Links field.

Args:
    table_id: The table ID containing the link field (e.g., "tbl_xxx")
    link_field_id: The Links field ID (e.g., "fld_xxx")
    record_id: The record ID to get linked records for
    fields: Comma-separated field names to include from linked records
    sort: Sort field(s), prefix with - for descending
    where: Filter condition for linked records

Returns:
    LinkedRecordsResult with linked records.

Example:
    # Get all tasks linked to a project
    linked_records_list("tbl_projects", "fld_tasks_link", "1")

```bash
nocodb call-tool linked_records_list --table-id <value> --link-field-id <value> --record-id <value> --fields <value> --sort <value> --where <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--link-field-id` | string | yes |  |
| `--record-id` | string | yes |  |
| `--fields` | string | no | JSON string |
| `--sort` | string | no | JSON string |
| `--where` | string | no | JSON string |

### linked_records_link

Link records together via a Links field.

Creates a relationship between the source record and target records.

Args:
    table_id: The table ID containing the link field (e.g., "tbl_xxx")
    link_field_id: The Links field ID (e.g., "fld_xxx")
    record_id: The source record ID to link from
    target_ids: List of record IDs to link to (e.g., ["1", "2", "3"])

Returns:
    LinkedRecordsResult with linked record references.

Example:
    # Link tasks 1, 2, 3 to project 5
    linked_records_link("tbl_projects", "fld_tasks_link", "5", ["1", "2", "3"])

```bash
nocodb call-tool linked_records_link --table-id <value> --link-field-id <value> --record-id <value> --target-ids <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--link-field-id` | string | yes |  |
| `--record-id` | string | yes |  |
| `--target-ids` | array[string] | yes |  |

### linked_records_unlink

Unlink records from a Links field relationship.

Removes the relationship between records. Does NOT delete the records themselves.

DESTRUCTIVE: Set confirm=True to proceed.

Args:
    table_id: The table ID containing the link field (e.g., "tbl_xxx")
    link_field_id: The Links field ID (e.g., "fld_xxx")
    record_id: The source record ID to unlink from
    target_ids: List of record IDs to unlink (e.g., ["1", "2"])
    confirm: Must be True to proceed with unlinking

Returns:
    LinkedRecordsResult with unlinked record references.

Example:
    # Unlink task 2 from project 5
    linked_records_unlink("tbl_projects", "fld_tasks_link", "5", ["2"], confirm=True)

```bash
nocodb call-tool linked_records_unlink --table-id <value> --link-field-id <value> --record-id <value> --target-ids <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--link-field-id` | string | yes |  |
| `--record-id` | string | yes |  |
| `--target-ids` | array[string] | yes |  |
| `--confirm` | boolean | no |  |

### views_list

List all views for a table.

Views include Grid, Gallery, Form, Kanban, and Calendar views.

Args:
    table_id: The table ID (e.g., "tbl_xxx")

Returns:
    ViewsListResult with list of views including id, title, and type.

View types (numeric):
    - 3: Grid
    - 4: Form
    - 5: Gallery
    - 6: Kanban
    - 7: Calendar

```bash
nocodb call-tool views_list --table-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |

### view_update

Update a view's metadata.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    title: New view title
    icon: View icon (emoji, e.g., "📊")
    meta: Additional metadata dict

Returns:
    ViewResult with updated view details.

```bash
nocodb call-tool view_update --view-id <value> --title <value> --icon <value> --meta <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--title` | string | no | JSON string |
| `--icon` | string | no | JSON string |
| `--meta` | string | no | JSON string |

### view_delete

Delete a view.

This only deletes the view, not the underlying data.
Records remain intact.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    confirm: Must be True to proceed with deletion

Returns:
    ViewDeleteResult with success status.

```bash
nocodb call-tool view_delete --view-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### view_filters_list

List all filters for a view.

Args:
    view_id: The view ID (e.g., "vw_xxx")

Returns:
    ViewFiltersListResult with list of filters.

```bash
nocodb call-tool view_filters_list --view-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |

### view_filter_get

Get details of a single filter.

Args:
    filter_id: The filter ID (e.g., "flt_xxx")

Returns:
    ViewFilterResult with filter details.

```bash
nocodb call-tool view_filter_get --filter-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--filter-id` | string | yes |  |

### view_filter_create

Create a new filter for a view.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    fk_column_id: The column/field ID to filter on (e.g., "fld_xxx")
    comparison_op: The comparison operator
    value: The filter value (not needed for null/empty checks)

Returns:
    ViewFilterResult with created filter details.

Comparison operators:
    - eq: Equal
    - neq: Not equal
    - like: Contains (use % wildcards)
    - nlike: Does not contain
    - gt: Greater than
    - lt: Less than
    - gte: Greater than or equal
    - lte: Less than or equal
    - is: Is null/notnull
    - isnot: Is not null
    - empty: Is empty
    - notempty: Is not empty
    - in: In array (comma-separated values)
    - notin: Not in array

Examples:
    - view_filter_create("vw_xxx", "fld_status", "eq", "Active")
    - view_filter_create("vw_xxx", "fld_age", "gt", 18)
    - view_filter_create("vw_xxx", "fld_email", "is", "notnull")

```bash
nocodb call-tool view_filter_create --view-id <value> --fk-column-id <value> --comparison-op <value> --value <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--fk-column-id` | string | yes |  |
| `--comparison-op` | string | yes |  |
| `--value` | string | no | JSON string |

### view_filter_update

Update an existing filter.

Args:
    filter_id: The filter ID (e.g., "flt_xxx")
    fk_column_id: New column/field ID
    comparison_op: New comparison operator
    value: New filter value

Returns:
    ViewFilterResult with updated filter details.

```bash
nocodb call-tool view_filter_update --filter-id <value> --fk-column-id <value> --comparison-op <value> --value <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--filter-id` | string | yes |  |
| `--fk-column-id` | string | no | JSON string |
| `--comparison-op` | string | no | JSON string |
| `--value` | string | no | JSON string |

### view_filter_delete

Delete a filter from a view.

Args:
    filter_id: The filter ID (e.g., "flt_xxx")
    confirm: Must be True to proceed with deletion

Returns:
    ViewFilterDeleteResult with success status.

```bash
nocodb call-tool view_filter_delete --filter-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--filter-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### view_filter_children

Get children filters of a filter group.

Filter groups allow nested AND/OR logic.

Args:
    filter_group_id: The parent filter group ID

Returns:
    ViewFiltersListResult with child filters.

```bash
nocodb call-tool view_filter_children --filter-group-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--filter-group-id` | string | yes |  |

### view_sorts_list

List all sorts for a view.

Args:
    view_id: The view ID (e.g., "vw_xxx")

Returns:
    ViewSortsListResult with list of sorts.

```bash
nocodb call-tool view_sorts_list --view-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |

### view_sort_get

Get details of a single sort.

Args:
    sort_id: The sort ID (e.g., "srt_xxx")

Returns:
    ViewSortResult with sort details.

```bash
nocodb call-tool view_sort_get --sort-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--sort-id` | string | yes |  |

### view_sort_create

Create a new sort for a view.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    fk_column_id: The column/field ID to sort by (e.g., "fld_xxx")
    direction: Sort direction - "asc" (ascending) or "desc" (descending)

Returns:
    ViewSortResult with created sort details.

```bash
nocodb call-tool view_sort_create --view-id <value> --fk-column-id <value> --direction <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--fk-column-id` | string | yes |  |
| `--direction` | string | no |  |

### view_sort_update

Update an existing sort.

Args:
    sort_id: The sort ID (e.g., "srt_xxx")
    fk_column_id: New column/field ID
    direction: New sort direction - "asc" or "desc"

Returns:
    ViewSortResult with updated sort details.

```bash
nocodb call-tool view_sort_update --sort-id <value> --fk-column-id <value> --direction <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--sort-id` | string | yes |  |
| `--fk-column-id` | string | no | JSON string |
| `--direction` | string | no | JSON string |

### view_sort_delete

Delete a sort from a view.

Args:
    sort_id: The sort ID (e.g., "srt_xxx")
    confirm: Must be True to proceed with deletion

Returns:
    ViewSortDeleteResult with success status.

```bash
nocodb call-tool view_sort_delete --sort-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--sort-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### view_columns_list

List all columns in a view with their visibility settings.

Args:
    view_id: The view ID (e.g., "vw_xxx")

Returns:
    ViewColumnsListResult with list of columns including show/order settings.

```bash
nocodb call-tool view_columns_list --view-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |

### view_column_update

Update a column's visibility or order in a view.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    column_id: The view column ID (from view_columns_list, not the field ID)
    show: Whether to show (True) or hide (False) the column
    order: Column position (0-indexed)

Returns:
    ViewColumnResult with updated column settings.

```bash
nocodb call-tool view_column_update --view-id <value> --column-id <value> --show <value> --order <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--column-id` | string | yes |  |
| `--show` | string | no | JSON string |
| `--order` | string | no | JSON string |

### view_columns_hide_all

Hide all columns in a view.

Useful for starting fresh and then selectively showing specific columns.

Args:
    view_id: The view ID (e.g., "vw_xxx")

Returns:
    ViewColumnsListResult with updated column visibility.

```bash
nocodb call-tool view_columns_hide_all --view-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |

### view_columns_show_all

Show all columns in a view.

Args:
    view_id: The view ID (e.g., "vw_xxx")

Returns:
    ViewColumnsListResult with updated column visibility.

```bash
nocodb call-tool view_columns_show_all --view-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |

### shared_views_list

List all shared (public) views for a table.

Args:
    table_id: The table ID (e.g., "tbl_xxx")

Returns:
    SharedViewsListResult with list of shared views.

```bash
nocodb call-tool shared_views_list --table-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |

### shared_view_create

Create a public link for a view.

This makes the view accessible via a unique URL without authentication.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    password: Optional password to protect the shared view

Returns:
    SharedViewResult with the UUID for the public URL.

Note: The full public URL will be: {nocodb_url}/shared/{uuid}

```bash
nocodb call-tool shared_view_create --view-id <value> --password <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--password` | string | no | JSON string |

### shared_view_update

Update a shared view's settings.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    password: New password (or None to remove password protection)

Returns:
    SharedViewResult with updated settings.

```bash
nocodb call-tool shared_view_update --view-id <value> --password <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--password` | string | no | JSON string |

### shared_view_delete

Remove public access from a view.

The public link will no longer work. The view itself is not deleted.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    confirm: Must be True to proceed with removal

Returns:
    SharedViewDeleteResult with success status.

```bash
nocodb call-tool shared_view_delete --view-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### webhooks_list

List all webhooks for a table.

Args:
    table_id: The table ID (e.g., "tbl_xxx")

Returns:
    WebhooksListResult with list of webhooks.

```bash
nocodb call-tool webhooks_list --table-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |

### webhook_delete

Delete a webhook.

Args:
    hook_id: The webhook ID (e.g., "hk_xxx")
    confirm: Must be True to proceed with deletion

Returns:
    WebhookDeleteResult with success status.

```bash
nocodb call-tool webhook_delete --hook-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--hook-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### webhook_logs

View execution logs for a webhook.

Useful for debugging webhook delivery issues.

Args:
    hook_id: The webhook ID (e.g., "hk_xxx")

Returns:
    WebhookLogsResult with list of execution logs.

```bash
nocodb call-tool webhook_logs --hook-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--hook-id` | string | yes |  |

### webhook_sample_payload

Get a sample webhook payload for testing.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    event: Event type - "records" (most common)
    operation: Operation type - "insert", "update", "delete"
    version: Payload version - "v1" or "v2" (default: "v2")

Returns:
    WebhookSamplePayloadResult with sample payload structure.

Example payload structure:
    {
        "event": "records",
        "operation": "insert",
        "row": {...},  # The affected record
        "table": {...},  # Table metadata
        ...
    }

```bash
nocodb call-tool webhook_sample_payload --table-id <value> --event <value> --operation <value> --version <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--event` | string | no |  |
| `--operation` | string | no |  |
| `--version` | string | no |  |

### webhook_filters_list

List filters for a webhook.

Webhook filters determine when the webhook triggers based on field values.

Args:
    hook_id: The webhook ID (e.g., "hk_xxx")

Returns:
    WebhookFiltersListResult with list of filters.

```bash
nocodb call-tool webhook_filters_list --hook-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--hook-id` | string | yes |  |

### webhook_filter_create

Create a filter for a webhook.

Filters control when the webhook fires based on field values.

Args:
    hook_id: The webhook ID (e.g., "hk_xxx")
    fk_column_id: The column/field ID to filter on
    comparison_op: The comparison operator (eq, neq, like, etc.)
    value: The filter value

Returns:
    WebhookFilterResult with created filter details.

Example:
    # Only trigger webhook when Status is "Completed"
    webhook_filter_create("hk_xxx", "fld_status", "eq", "Completed")

```bash
nocodb call-tool webhook_filter_create --hook-id <value> --fk-column-id <value> --comparison-op <value> --value <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--hook-id` | string | yes |  |
| `--fk-column-id` | string | yes |  |
| `--comparison-op` | string | yes |  |
| `--value` | string | no | JSON string |

### members_list

List all members of the current base.

Returns:
    MembersListResult with list of members including id, email, and roles.

```bash
nocodb call-tool members_list
```

### member_add

Add a new member to the current base.

Args:
    email: The user's email address
    role: The role to assign. Options:
        - owner: Full control
        - creator: Can create tables
        - editor: Can edit records
        - commenter: Can comment only
        - viewer: Read-only access

Returns:
    MemberResult with the added member details.

```bash
nocodb call-tool member_add --email <value> --role <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--email` | string | yes |  |
| `--role` | string | no |  |

### member_update

Update a member's role.

Args:
    member_id: The member ID
    role: The new role. Options:
        - owner: Full control
        - creator: Can create tables
        - editor: Can edit records
        - commenter: Can comment only
        - viewer: Read-only access

Returns:
    MemberResult with updated member details.

```bash
nocodb call-tool member_update --member-id <value> --role <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--member-id` | string | yes |  |
| `--role` | string | yes |  |

### member_remove

Remove a member from the base.

The user will lose access to this base but their NocoDB account
is not affected.

Args:
    member_id: The member ID to remove
    confirm: Must be True to proceed with removal

Returns:
    MemberDeleteResult with success status.

```bash
nocodb call-tool member_remove --member-id <value> --confirm
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--member-id` | string | yes |  |
| `--confirm` | boolean | no |  |

### attachment_upload

Upload a file attachment to a record's Attachment field.

The file content must be provided as base64-encoded data.

Args:
    table_id: The table ID (e.g., "tbl_xxx")
    record_id: The record ID to attach the file to
    field_id: The Attachment field ID (e.g., "fld_xxx")
    filename: The filename for the uploaded file (e.g., "document.pdf")
    content_base64: Base64-encoded file content
    content_type: MIME type of the file (e.g., "application/pdf", "image/png")

Returns:
    AttachmentUploadResult with URL and metadata.

Example:
    # Upload a small text file
    import base64
    content = base64.b64encode(b"Hello World").decode()
    attachment_upload("tbl_xxx", "1", "fld_attach", "hello.txt", content, "text/plain")

Common MIME types:
    - application/pdf
    - image/png, image/jpeg, image/gif
    - text/plain, text/csv
    - application/json
    - application/vnd.openxmlformats-officedocument.spreadsheetml.sheet (xlsx)

```bash
nocodb call-tool attachment_upload --table-id <value> --record-id <value> --field-id <value> --filename <value> --content-base64 <value> --content-type <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |
| `--record-id` | string | yes |  |
| `--field-id` | string | yes |  |
| `--filename` | string | yes |  |
| `--content-base64` | string | yes |  |
| `--content-type` | string | yes |  |

### storage_upload

Upload a file to NocoDB general storage.

This uploads a file to storage without attaching it to a specific record.
Useful for assets that need to be referenced across multiple records.

Args:
    filename: The filename (e.g., "logo.png", "document.pdf")
    content_base64: Base64-encoded file content
    content_type: Optional MIME type (auto-detected if not provided)

Returns:
    StorageUploadResult with URL and metadata.

For attaching files to specific record fields, use attachment_upload instead.

Common MIME types:
    - application/pdf
    - image/png, image/jpeg, image/gif
    - text/plain, text/csv
    - application/json

```bash
nocodb call-tool storage_upload --filename <value> --content-base64 <value> --content-type <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--filename` | string | yes |  |
| `--content-base64` | string | yes |  |
| `--content-type` | string | no | JSON string |

### export_csv

Export a view's data as CSV.

Args:
    view_id: The view ID (e.g., "vw_xxx")
    offset: Row offset for pagination (skip first N rows)
    limit: Maximum number of rows to export

Returns:
    ExportResult with CSV content as a string.

Note: For large datasets, use offset and limit for pagination
to avoid timeouts.

Example:
    # Export first 100 rows
    export_csv("vw_xxx", limit=100)

    # Export rows 101-200
    export_csv("vw_xxx", offset=100, limit=100)

```bash
nocodb call-tool export_csv --view-id <value> --offset <value> --limit <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--view-id` | string | yes |  |
| `--offset` | string | no | JSON string |
| `--limit` | string | no | JSON string |

### schema_export_table

Export portable schema for a single table.

Returns a clean schema with system fields and internal IDs removed,
suitable for documentation or recreating the table structure.

Args:
    table_id: The table ID (e.g., "tbl_xxx")

Returns:
    TableSchemaResult with title and fields array.
    Each field contains type, title, and field-specific options.

Example output:
    {
        "title": "Users",
        "fields": [
            {"title": "Name", "type": "SingleLineText"},
            {"title": "Email", "type": "Email"},
            {"title": "Status", "type": "SingleSelect", "colOptions": {...}}
        ]
    }

```bash
nocodb call-tool schema_export_table --table-id <value>
```

| Flag | Type | Required | Description |
|------|------|----------|-------------|
| `--table-id` | string | yes |  |

### schema_export_base

Export portable schema for the entire base with all tables.

Returns a clean schema with system fields and internal IDs removed,
suitable for documentation or recreating the base structure.

Returns:
    BaseSchemaResult with title, description, and tables array.
    Each table contains title and fields array.

Example output:
    {
        "title": "My Project",
        "description": "Project database",
        "tables": [
            {
                "title": "Users",
                "fields": [...]
            },
            {
                "title": "Tasks",
                "fields": [...]
            }
        ]
    }

```bash
nocodb call-tool schema_export_base
```

### get_workflow_guide

Get the NocoDB workflow guide - CRITICAL rules for schema discovery.

IMPORTANT: This is internal documentation for your reference only.
Do NOT paste this content into the chat. Read it, internalize the rules,
and apply them silently. Only mention specific rules if the user asks.

Call this BEFORE your first NocoDB query to learn the required workflow:
1. tables_list -> Get table IDs
2. fields_list(table_id) -> REQUIRED before sort/where
3. records_list(...) -> Query using actual field names

Returns:
    Markdown guide with workflow rules (for internal use).

```bash
nocodb call-tool get_workflow_guide
```

### get_reference

Get the complete NocoDB MCP reference documentation.

IMPORTANT: This is internal documentation for your reference only.
Do NOT paste this content into the chat. Use it to look up syntax,
field types, or tool parameters when needed. Only share specific
details if the user explicitly asks.

Contains:
- Tool descriptions by category
- Field type reference with options
- Filter syntax guide
- Common workflow examples

Returns:
    Full markdown reference (for internal use).

```bash
nocodb call-tool get_reference
```

## Utility Commands

```bash
nocodb list-tools
nocodb list-resources
nocodb read-resource <uri>
nocodb list-prompts
nocodb get-prompt <name> [key=value ...]
```
