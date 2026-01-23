# Migration Guide: v2 to v3

This guide documents breaking changes when migrating from the v1/v2 API to the v3 API in the NocoDB Python client.

## Overview

The v3 API introduces several important changes:

1. **ID-based routing** - Uses `base_id` and `table_id` instead of `org/project/table` paths
2. **Nested response format** - Records use `{id, fields}` structure instead of flat objects
3. **Batch operations** - Create, update, and delete accept arrays by default
4. **Renamed filter operators** - `ge`/`le` become `gte`/`lte`
5. **Hybrid v2/v3 approach** - Some meta operations require v2 API (self-hosted limitations)

## Quick Start

**Before (v1 API):**
```python
from nocodb import NocoDBProject
from nocodb.infra.requests_client import NocoDBRequestsClient

client = NocoDBRequestsClient(APIToken("token"), "http://localhost:8080")
project = NocoDBProject("noco", "my_project")

# List records
rows = client.table_row_list(project, "users")
for row in rows["list"]:
    print(row["Name"])  # Flat field access

# Create record
new_row = client.table_row_create(project, "users", {"Name": "John"})
```

**After (v3 API):**
```python
from nocodb import NocoDBBase, APIToken
from nocodb.infra.requests_client import NocoDBRequestsClient

client = NocoDBRequestsClient(APIToken("token"), "http://localhost:8080")
base_id = "pgfqcp0ocloo1j3"
table_id = "mq31p5ngbwj5o7u"

# List records
result = client.records_list_v3(base_id, table_id)
for record in result["records"]:
    print(record["fields"]["Name"])  # Nested field access

# Create record (batch format)
new_records = client.records_create_v3(base_id, table_id, [
    {"fields": {"Name": "John"}}
])
```

## Breaking Changes

### Class Changes

| v1 Class | v3 Class | Notes |
|----------|----------|-------|
| `NocoDBProject(org, project_name)` | `NocoDBBase(base_id)` | `NocoDBProject` still works but emits deprecation warning |

**v1 API:**
```python
from nocodb import NocoDBProject

project = NocoDBProject("noco", "my_project")
# Uses project.org_name and project.project_name internally
```

**v3 API:**
```python
from nocodb import NocoDBBase

base = NocoDBBase("pgfqcp0ocloo1j3")
# Or with optional workspace_id
base = NocoDBBase("pgfqcp0ocloo1j3", workspace_id="ws_abc123")

# Access the base_id
print(base.base_id)  # "pgfqcp0ocloo1j3"
```

**Backwards compatibility:**
```python
# NocoDBProject still works but emits DeprecationWarning
from nocodb import NocoDBProject

# Legacy positional args
project = NocoDBProject("noco", "my_project")

# Or keyword args
project = NocoDBProject(base_id="pgfqcp0ocloo1j3", workspace_id="ws_abc")
```

### Method Changes

#### Record Operations

| v1 Method | v3 Method |
|-----------|-----------|
| `table_row_list(project, table)` | `records_list_v3(base_id, table_id)` |
| `table_row_detail(project, table, row_id)` | `record_get_v3(base_id, table_id, record_id)` |
| `table_row_create(project, table, body)` | `records_create_v3(base_id, table_id, records)` |
| `table_row_update(project, table, row_id, body)` | `records_update_v3(base_id, table_id, records)` |
| `table_row_delete(project, table, row_id)` | `records_delete_v3(base_id, table_id, record_ids)` |
| `table_count(project, table)` | `records_count_v3(base_id, table_id)` |
| `table_row_nested_relations_list(...)` | `linked_records_list_v3(base_id, table_id, link_field_id, record_id)` |

#### Meta Operations

| v1 Method | v3 Method |
|-----------|-----------|
| `table_list(project)` | `tables_list_v3(base_id)` |
| N/A | `bases_list_v3()` (uses v2 API internally for self-hosted) |
| N/A | `views_list(table_id)` (v2 API) |
| N/A | `view_filters_list(view_id)` (v2 API) |
| N/A | `view_sorts_list(view_id)` (v2 API) |

### Response Format Changes

#### Single Record

**v1 Response (flat):**
```json
{
  "Id": 1,
  "Name": "John Doe",
  "Email": "john@example.com",
  "CreatedAt": "2024-01-15T10:30:00.000Z"
}
```

**v3 Response (nested):**
```json
{
  "id": 1,
  "fields": {
    "Name": "John Doe",
    "Email": "john@example.com",
    "CreatedAt": "2024-01-15T10:30:00.000Z"
  }
}
```

**Migration:**
```python
# v1: Direct field access
name = record["Name"]

# v3: Access through fields
name = record["fields"]["Name"]
```

#### List Response

**v1 Response:**
```json
{
  "list": [
    {"Id": 1, "Name": "John"},
    {"Id": 2, "Name": "Jane"}
  ],
  "pageInfo": {
    "totalRows": 100,
    "page": 1,
    "pageSize": 25
  }
}
```

**v3 Response:**
```json
{
  "records": [
    {"id": 1, "fields": {"Name": "John"}},
    {"id": 2, "fields": {"Name": "Jane"}}
  ],
  "next": "http://localhost:8080/api/v3/data/.../records?page=2"
}
```

**Migration:**
```python
# v1: Access list key
for row in result["list"]:
    print(row["Name"])

# v3: Access records key with nested fields
for record in result["records"]:
    print(record["fields"]["Name"])

# Pagination
# v1: Use pageInfo.totalRows, pageInfo.page
# v3: Follow "next" URL if present
if result.get("next"):
    # Fetch next page
    pass
```

### Filter Changes

#### Operator Renames

| v1 Operator | v3 Operator | Filter Class |
|-------------|-------------|--------------|
| `ge` | `gte` | `GreaterOrEqualFilter` |
| `le` | `lte` | `LessOrEqualFilter` |

**Migration:**
```python
# v1: Old operator names
from nocodb.filters import GreaterOrEqualFilter, LessOrEqualFilter

# These filters now use v3 operators automatically
ge_filter = GreaterOrEqualFilter("Age", 18)  # Generates: (Age,gte,18)
le_filter = LessOrEqualFilter("Age", 65)     # Generates: (Age,lte,65)
```

#### New Filter Types (v3 Only)

```python
from nocodb.filters import IsFilter, InFilter, BetweenFilter, NotLikeFilter

# IsFilter - null/empty checks
IsFilter("Status", "null")       # (Status,is,null)
IsFilter("Status", "notnull")    # (Status,is,notnull)
IsFilter("Active", "true")       # (Active,is,true)
IsFilter("Active", "false")      # (Active,is,false)
IsFilter("Notes", "empty")       # (Notes,is,empty)
IsFilter("Notes", "notempty")    # (Notes,is,notempty)

# InFilter - match list of values
InFilter("Tags", ["urgent", "important"])  # (Tags,in,urgent,important)
InFilter("Status", ["open", "pending"])    # (Status,in,open,pending)

# BetweenFilter - range matching
BetweenFilter("Age", 18, 65)                       # (Age,btw,18,65)
BetweenFilter("Date", "2024-01-01", "2024-12-31")  # (Date,btw,2024-01-01,2024-12-31)

# NotLikeFilter - does not contain
NotLikeFilter("Name", "%test%")  # (Name,nlike,%test%)
```

#### Filter Syntax

The logical operator syntax remains the same (`~and`, `~or`, `~not`):

```python
from nocodb.filters import EqFilter, LikeFilter, And, Or, Not

# AND filter
filter1 = And(
    EqFilter("Status", "Active"),
    LikeFilter("Name", "%test%")
)
# Generates: (Status,eq,Active)~and(Name,like,%test%)

# OR filter
filter2 = Or(
    EqFilter("Status", "Active"),
    EqFilter("Status", "Pending")
)
# Generates: (Status,eq,Active)~or(Status,eq,Pending)

# NOT filter
filter3 = Not(EqFilter("Status", "Deleted"))
# Generates: ~not(Status,eq,Deleted)

# Using filters
result = client.records_list_v3(base_id, table_id, params={
    "where": filter1.get_where()
})
```

### Batch Operations

v3 methods accept arrays for batch operations, unlike v1 which operated on single records.

#### Create (Batch)

```python
# v1: Single record
new_row = client.table_row_create(project, "users", {
    "Name": "John"
})

# v3: Batch create (accepts array)
new_records = client.records_create_v3(base_id, table_id, [
    {"fields": {"Name": "John"}},
    {"fields": {"Name": "Jane"}},
    {"fields": {"Name": "Bob"}}
])
# Returns: [{"id": 1, "fields": {...}}, {"id": 2, "fields": {...}}, ...]

# Single record still works (auto-wrapped in array)
new_record = client.records_create_v3(base_id, table_id,
    {"fields": {"Name": "John"}}
)
```

#### Update (Batch)

```python
# v1: Single record with ID in URL
client.table_row_update(project, "users", 1, {
    "Name": "John Updated"
})

# v3: Batch update with IDs in payload
updated = client.records_update_v3(base_id, table_id, [
    {"id": 1, "fields": {"Name": "John Updated"}},
    {"id": 2, "fields": {"Name": "Jane Updated"}}
])

# Single record (auto-wrapped)
updated = client.records_update_v3(base_id, table_id,
    {"id": 1, "fields": {"Name": "John Updated"}}
)
```

#### Delete (Batch)

```python
# v1: Single record
client.table_row_delete(project, "users", 1)

# v3: Batch delete with array of IDs
deleted = client.records_delete_v3(base_id, table_id, [1, 2, 3])
# Returns: [{"id": 1}, {"id": 2}, {"id": 3}]

# Single record (auto-wrapped)
deleted = client.records_delete_v3(base_id, table_id, 1)
```

### Linked Records

```python
# v1: Nested relations
linked = client.table_row_nested_relations_list(
    project,
    "orders",
    "mm",          # relation_type: mm, hm, bt
    1,             # row_id
    "Products"     # column_name
)

# v3: Linked records with field ID
linked = client.linked_records_list_v3(
    base_id,
    table_id,
    "lk_abc123",   # link_field_id
    1              # record_id
)
# Response: {"list": [{"id": 22, "fields": {...}}], "next": "url"}

# Link records
client.linked_records_link_v3(
    base_id, table_id, "lk_abc123", 1,
    link_records=[{"id": 22}, {"id": 43}]
)

# Unlink records
client.linked_records_unlink_v3(
    base_id, table_id, "lk_abc123", 1,
    unlink_records=[{"id": 22}]
)
```

## API Version Split

This client uses a hybrid v2/v3 approach because some v3 endpoints are Enterprise-only in self-hosted NocoDB.

| Feature | API Version | Endpoint | Notes |
|---------|-------------|----------|-------|
| Records CRUD | v3 | `/api/v3/data/{baseId}/{tableId}/records` | Full support |
| Linked Records | v3 | `/api/v3/data/{baseId}/{tableId}/links/...` | Full support |
| Attachments | v3 | `/api/v3/data/.../upload` | Full support |
| List Bases | v2 | `/api/v2/meta/bases` | v3 requires Enterprise |
| Get/Update/Delete Base | v3 | `/api/v3/meta/bases/{baseId}` | Works in community |
| Tables CRUD | v3 | `/api/v3/meta/bases/{baseId}/tables` | Full support |
| Fields CRUD | v3 | `/api/v3/meta/bases/{baseId}/tables/{tableId}/fields` | Full support |
| Views CRUD | v2 | `/api/v2/meta/tables/{tableId}/views` | v3 requires Enterprise |
| View Filters | v2 | `/api/v2/meta/views/{viewId}/filters` | v3 requires Enterprise |
| View Sorts | v2 | `/api/v2/meta/views/{viewId}/sorts` | v3 requires Enterprise |
| Webhooks | v2 | `/api/v2/meta/tables/{tableId}/hooks` | Not yet in v3 |

## Backwards Compatibility

### Deprecated Aliases

The following classes and methods work but emit `DeprecationWarning`:

```python
# NocoDBProject -> NocoDBBase
from nocodb import NocoDBProject  # Deprecated
project = NocoDBProject("noco", "my_project")
# Warning: NocoDBProject is deprecated. Use NocoDBBase instead.

# Legacy methods still available
client.table_row_list(project, "table")     # Deprecated
client.table_row_create(project, "table", body)  # Deprecated
client.table_list(project)                  # Deprecated
```

### Property Aliases

`NocoDBBase` provides deprecated property aliases for old code:

```python
from nocodb import NocoDBBase

base = NocoDBBase("pgfqcp0ocloo1j3", workspace_id="ws_abc")

# New properties (recommended)
base.base_id        # "pgfqcp0ocloo1j3"
base.workspace_id   # "ws_abc"

# Deprecated properties (emit warnings)
base.project_name   # "pgfqcp0ocloo1j3" (DeprecationWarning)
base.org_name       # "ws_abc" (DeprecationWarning)
```

### Suppressing Warnings

If migrating gradually, you can suppress deprecation warnings:

```python
import warnings

# Suppress all deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Or suppress only nocodb warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="nocodb")
```

## Enterprise-Only Features

These features require NocoDB Enterprise and are NOT available in self-hosted community edition:

- **Workspaces** - Multi-tenant hierarchy above bases
- **Teams** - Team management
- **Workspace members** - Member management within workspaces
- **v3 Views API** - Use v2 `views_list()` instead
- **v3 Bases list** - Use v2 `bases_list_v3()` (which internally uses v2)

The client provides stubs for some Enterprise features but they will fail on self-hosted:

```python
# This will fail on self-hosted community edition
try:
    workspaces = client.workspaces_list_v3()
except NocoDBAPIError as e:
    print(f"Enterprise feature: {e}")
```

## Migration Checklist

1. [ ] Replace `NocoDBProject` with `NocoDBBase` or use raw `base_id` string
2. [ ] Update method calls from `table_row_*` to `*_v3` methods
3. [ ] Change response parsing from `result["list"]` to `result["records"]`
4. [ ] Update field access from `record["Field"]` to `record["fields"]["Field"]`
5. [ ] Convert single record operations to batch format
6. [ ] Update filter operator usage (`ge` -> `gte`, `le` -> `lte`)
7. [ ] Replace nested relations with `linked_records_*_v3` methods
8. [ ] Test with deprecation warnings enabled to find remaining issues

## Example: Full Migration

**Before:**
```python
from nocodb import NocoDBProject, APIToken
from nocodb.infra.requests_client import NocoDBRequestsClient
from nocodb.filters import EqFilter, GreaterOrEqualFilter

client = NocoDBRequestsClient(APIToken("token"), "http://localhost:8080")
project = NocoDBProject("noco", "my_project")

# List active users over 18
filter_condition = And(
    EqFilter("Status", "Active"),
    GreaterOrEqualFilter("Age", 18)
)
result = client.table_row_list(project, "users", filter_obj=filter_condition)

for row in result["list"]:
    print(f"{row['Name']} - {row['Email']}")

# Create user
new_user = client.table_row_create(project, "users", {
    "Name": "John Doe",
    "Email": "john@example.com"
})
print(f"Created user ID: {new_user['Id']}")

# Update user
client.table_row_update(project, "users", new_user["Id"], {
    "Status": "Verified"
})

# Delete user
client.table_row_delete(project, "users", new_user["Id"])
```

**After:**
```python
from nocodb import NocoDBBase, APIToken
from nocodb.infra.requests_client import NocoDBRequestsClient
from nocodb.filters import EqFilter, GreaterOrEqualFilter, And

client = NocoDBRequestsClient(APIToken("token"), "http://localhost:8080")
base_id = "pgfqcp0ocloo1j3"
table_id = "mq31p5ngbwj5o7u"

# List active users over 18
filter_condition = And(
    EqFilter("Status", "Active"),
    GreaterOrEqualFilter("Age", 18)
)
result = client.records_list_v3(base_id, table_id, params={
    "where": filter_condition.get_where()
})

for record in result["records"]:
    print(f"{record['fields']['Name']} - {record['fields']['Email']}")

# Create user (batch format)
new_users = client.records_create_v3(base_id, table_id, [
    {"fields": {"Name": "John Doe", "Email": "john@example.com"}}
])
new_user = new_users[0]
print(f"Created user ID: {new_user['id']}")

# Update user (batch format with ID in payload)
client.records_update_v3(base_id, table_id, [
    {"id": new_user["id"], "fields": {"Status": "Verified"}}
])

# Delete user
client.records_delete_v3(base_id, table_id, [new_user["id"]])
```
