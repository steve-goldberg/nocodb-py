# NocoDB Python Client

Python client for NocoDB API - **Self-hosted community edition**.

NocoDB is an open-source Airtable alternative. This client provides a simple Python interface for the NocoDB REST API.

## Features

- Full v3 Data API support (records, links, attachments)
- v3 Meta API for tables and fields
- v2 Meta API for bases list, views, filters, sorts, webhooks
- Query filters with logical operators
- Batch operations support
- MIT licensed

## API Version Summary

This client uses a hybrid v2/v3 approach based on self-hosted NocoDB availability:

| Feature | API | Notes |
|---------|-----|-------|
| Records CRUD | v3 | Full support |
| Linked Records | v3 | Link/unlink operations |
| Attachments | v3 | File uploads |
| List Bases | v2 | v3 requires Enterprise |
| Get/Update/Delete Base | v3 | Works in community |
| Tables CRUD | v3 | Full support |
| Fields CRUD | v3 | Full support |
| Views CRUD | v2 | v3 requires Enterprise |
| View Filters/Sorts | v2 | v3 requires Enterprise |
| Webhooks | v2 | Not yet in v3 |

## Installation

```bash
pip install nocodb
```

## Quick Start

### Client Setup

```python
from nocodb import NocoDBBase, APIToken
from nocodb.infra.requests_client import NocoDBRequestsClient

# Create client with API token
client = NocoDBRequestsClient(
    APIToken("YOUR-API-TOKEN"),
    "http://localhost:8080"  # Your NocoDB instance URL
)

# Define base and table IDs (from NocoDB URL or API)
base_id = "pgfqcp0ocloo1j3"    # e.g., from URL: /dashboard/#/nc/pgfqcp0ocloo1j3
table_id = "mq31p5ngbwj5o7u"   # e.g., from table settings
```

### v3 Data API - Records

```python
# List records
result = client.records_list_v3(base_id, table_id)
# Response: {"records": [{"id": 1, "fields": {"Name": "...", "Status": "..."}}], "next": "..."}

# Access records from response
for record in result["records"]:
    print(f"ID: {record['id']}, Name: {record['fields']['Name']}")

# Get single record
record = client.record_get_v3(base_id, table_id, 1)
# Response: {"id": 1, "fields": {"Name": "John", "Status": "Active"}}

# Create records (batch)
new_records = client.records_create_v3(base_id, table_id, [
    {"fields": {"Name": "Record 1", "Status": "Active"}},
    {"fields": {"Name": "Record 2", "Status": "Draft"}}
])
# Response: [{"id": 1, "fields": {...}}, {"id": 2, "fields": {...}}]

# Update records (batch)
updated = client.records_update_v3(base_id, table_id, [
    {"id": 1, "fields": {"Status": "Complete"}},
    {"id": 2, "fields": {"Status": "Active"}}
])

# Delete records (batch)
deleted = client.records_delete_v3(base_id, table_id, [1, 2])
# Response: [{"id": 1}, {"id": 2}]

# Count records
count_result = client.records_count_v3(base_id, table_id)
# Response: {"count": 42}
```

### Query Parameters

The v3 API accepts query parameters for filtering, sorting, and pagination:

```python
# Pagination
result = client.records_list_v3(base_id, table_id, params={
    "page": 1,
    "pageSize": 25
})

# Select specific fields
result = client.records_list_v3(base_id, table_id, params={
    "fields": "Name,Status,CreatedAt"
})

# Sort records (prefix with - for descending)
result = client.records_list_v3(base_id, table_id, params={
    "sort": "-CreatedAt,Name"
})

# Filter with view
result = client.records_list_v3(base_id, table_id, params={
    "viewId": "vw_abc123"
})
```

### Filtering Records

Use the filter classes to build query conditions:

```python
from nocodb.filters import EqFilter, LikeFilter, And, Or, IsFilter, InFilter, BetweenFilter

# Simple filter - pass to params["where"]
result = client.records_list_v3(base_id, table_id, params={
    "where": EqFilter("Status", "Active").get_where()
})
# Generates: (Status,eq,Active)

# Combined filters with And/Or
filter_condition = And(
    EqFilter("Status", "Active"),
    LikeFilter("Name", "%test%")
)
result = client.records_list_v3(base_id, table_id, params={
    "where": filter_condition.get_where()
})
# Generates: (Status,eq,Active)~and(Name,like,%test%)

# Or conditions
filter_condition = Or(
    EqFilter("Status", "Active"),
    EqFilter("Status", "Pending")
)
# Generates: (Status,eq,Active)~or(Status,eq,Pending)

# Null/empty checks with IsFilter
result = client.records_list_v3(base_id, table_id, params={
    "where": IsFilter("Status", "notnull").get_where()
})
# Valid values: null, notnull, true, false, empty, notempty

# Match list of values with InFilter
result = client.records_list_v3(base_id, table_id, params={
    "where": InFilter("Tags", ["urgent", "important"]).get_where()
})
# Generates: (Tags,in,urgent,important)

# Range matching with BetweenFilter
result = client.records_list_v3(base_id, table_id, params={
    "where": BetweenFilter("Age", 18, 65).get_where()
})
# Generates: (Age,btw,18,65)
```

### v3 Linked Records

```python
link_field_id = "lk_abc123"
record_id = 1

# List linked records
linked = client.linked_records_list_v3(base_id, table_id, link_field_id, record_id)
# Response: {"list": [{"id": 22, "fields": {...}}], "next": "url"}

# Link records
client.linked_records_link_v3(base_id, table_id, link_field_id, record_id,
    link_records=[{"id": 22}, {"id": 43}])

# Unlink records
client.linked_records_unlink_v3(base_id, table_id, link_field_id, record_id,
    unlink_records=[{"id": 22}])
```

### v2 Meta API - Bases & Views

```python
# List all bases (v2 API - required for self-hosted)
bases = client.bases_list_v3()
# Response: {"list": [{"id": "base_abc", "title": "My Base"}]}

# List views for a table (v2 API)
views = client.views_list(table_id)

# Get view filters (v2 API)
filters = client.view_filters_list(view_id)

# Get view sorts (v2 API)
sorts = client.view_sorts_list(view_id)
```

### v3 Meta API - Tables & Fields

```python
# List tables in a base
tables = client.tables_list_v3(base_id)
# Response: {"tables": [{"id": "tbl_abc", "title": "My Table"}]}

# Get table schema
table_meta = client.table_get_v3(base_id, table_id)

# List fields
fields = client.fields_list_v3(base_id, table_id)
```

## Available Filters

### Comparison Filters

| Filter | Operator | Description |
|--------|----------|-------------|
| `EqFilter` / `EqualFilter` | `eq` | Equal |
| `NotEqualFilter` | `neq` | Not equal |
| `GreaterThanFilter` | `gt` | Greater than |
| `GreaterOrEqualFilter` | `gte` | Greater than or equal |
| `LessThanFilter` | `lt` | Less than |
| `LessOrEqualFilter` | `lte` | Less than or equal |
| `LikeFilter` | `like` | Contains (use `%` wildcard) |
| `NotLikeFilter` | `nlike` | Does not contain |

### Special Filters

| Filter | Operator | Description |
|--------|----------|-------------|
| `IsFilter` | `is` | Null/empty checks: `null`, `notnull`, `true`, `false`, `empty`, `notempty` |
| `InFilter` | `in` | Match list of values |
| `BetweenFilter` | `btw` | Range matching |

### Logical Operators

| Operator | v3 Syntax | Description |
|----------|-----------|-------------|
| `And` | `~and` | Combine filters with AND |
| `Or` | `~or` | Combine filters with OR |
| `Not` | `~not` | Negate a filter |

### Custom Filters

```python
from nocodb.filters.factory import basic_filter_class_factory
from nocodb.filters.raw_filter import RawFilter

# Create custom filter class
CustomFilter = basic_filter_class_factory('custom_op')
my_filter = CustomFilter("field", "value")
# Generates: (field,custom_op,value)

# Or use raw filter string directly
result = client.records_list_v3(base_id, table_id, params={
    "where": RawFilter('(field,op,value)').get_where()
})
```

## v3 Response Format

The v3 API returns records in a nested format with `id` and `fields`:

```python
# v3 record structure
{
    "id": 1,
    "fields": {
        "Name": "John Doe",
        "Email": "john@example.com",
        "Status": "Active",
        "CreatedAt": "2024-01-15T10:30:00.000Z"
    }
}

# v3 list response
{
    "records": [
        {"id": 1, "fields": {"Name": "John", ...}},
        {"id": 2, "fields": {"Name": "Jane", ...}}
    ],
    "next": "http://localhost:8080/api/v3/data/.../records?page=2"  # Optional pagination URL
}
```

## Breaking Changes from v1

| Aspect | v1 API | v3 API |
|--------|--------|--------|
| Base identifier | `NocoDBProject(org, project_name)` | `NocoDBBase(base_id)` or just `base_id` string |
| List records | `table_row_list(project, table)` | `records_list_v3(base_id, table_id)` |
| Get record | `table_row_detail(project, table, row_id)` | `record_get_v3(base_id, table_id, record_id)` |
| Create record | `table_row_create(project, table, body)` | `records_create_v3(base_id, table_id, records)` |
| Update record | `table_row_update(project, table, row_id, body)` | `records_update_v3(base_id, table_id, records)` |
| Delete record | `table_row_delete(project, table, row_id)` | `records_delete_v3(base_id, table_id, record_ids)` |
| Response format | `{"Id": 1, "Name": "..."}` | `{"id": 1, "fields": {"Name": "..."}}` |
| Filter operators | `ge`, `le` | `gte`, `lte` |

### Migration Example

```python
# v1 API (deprecated)
from nocodb import NocoDBProject
project = NocoDBProject("noco", "my_project")
rows = client.table_row_list(project, "users")

# v3 API (recommended)
base_id = "pgfqcp0ocloo1j3"
table_id = "mq31p5ngbwj5o7u"
result = client.records_list_v3(base_id, table_id)
records = result["records"]
```

## Not Supported (Enterprise Only)

These features require NocoDB Enterprise and are not available in self-hosted community edition:

- Workspaces (multi-tenant hierarchy)
- Teams management
- Workspace members
- v3 Views API
- v3 Bases list endpoint

## License

MIT

## Contributing

See [contributors.md](contributors.md) for guidelines.
