# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python client for NocoDB API - **Self-hosted community edition only**.

**Status:** v3.0.0 - Feature complete (37/37 features, 138 tests)

This client uses a hybrid v2/v3 API approach based on what's available in self-hosted NocoDB:
- **v3 Data API** - Records CRUD, links, attachments, button actions
- **v3 Meta API** - Tables, fields, base CRUD, base members
- **v2 Meta API** - List bases, views, view filters/sorts, webhooks

Use `/nocodbv3` skill for NocoDB API documentation when implementing features.

## API Version Reference

| Feature | API Version | Endpoint Pattern |
|---------|-------------|------------------|
| Records CRUD | v3 | `/api/v3/data/{baseId}/{tableId}/records` |
| Linked Records | v3 | `/api/v3/data/{baseId}/{tableId}/links/{linkFieldId}/{recordId}` |
| Attachments | v3 | `/api/v3/data/{baseId}/{tableId}/records/{recordId}/fields/{fieldId}/upload` |
| Button Actions | v3 | `/api/v3/data/{baseId}/{tableId}/actions/{columnId}` |
| List Bases | v2 | `/api/v2/meta/bases` |
| Get/Update/Delete Base | v3 | `/api/v3/meta/bases/{baseId}` |
| Base Members | v3 | `/api/v3/meta/bases/{baseId}/members` |
| Tables CRUD | v3 | `/api/v3/meta/bases/{baseId}/tables` |
| Fields CRUD | v3 | `/api/v3/meta/bases/{baseId}/tables/{tableId}/fields` |
| Field Read | v3 | `/api/v3/meta/bases/{baseId}/fields/{fieldId}` |
| Views CRUD | v2 | `/api/v2/meta/tables/{tableId}/views` |
| View Filters | v2 | `/api/v2/meta/views/{viewId}/filters` |
| View Sorts | v2 | `/api/v2/meta/views/{viewId}/sorts` |
| Webhooks | v2 | `/api/v2/meta/tables/{tableId}/hooks` |

## Commands

```bash
# Setup environment
./init.sh

# Install in development mode (with venv active)
source venv/bin/activate
pip install -e .

# Run all tests
python -m pytest nocodb/ -v

# Run single test file
python -m pytest nocodb/filters/filters_test.py -v

# Run specific test
python -m pytest nocodb/filters/filters_test.py::test_or_filter -v
```

## Directory Structure

```
nocodb-api-v3-client/
├── nocodb/
│   ├── __init__.py           # Package exports, version (3.0.0)
│   ├── nocodb.py             # Core domain models (NocoDBBase, NocoDBClient, WhereFilter)
│   ├── api.py                # URI builders (v3 + deprecated v1)
│   ├── exceptions.py         # Custom exceptions
│   ├── utils.py              # Utility functions
│   ├── filters/
│   │   ├── __init__.py       # Filter exports (EqFilter, IsFilter, InFilter, BetweenFilter, etc.)
│   │   ├── factory.py        # basic_filter_class_factory()
│   │   ├── logical.py        # And, Or, Not operators
│   │   ├── raw_filter.py     # RawFilter for custom strings
│   │   └── *_test.py         # Colocated unit tests (filters_test, factory_test, logical_test)
│   └── infra/
│       ├── __init__.py
│       ├── requests_client.py      # HTTP client (v3 + legacy methods)
│       └── requests_client_test.py # Unit tests (138 tests)
├── tests/
│   ├── integration_examples.py     # Integration examples (manual)
│   └── test_integration_full.py    # Full integration tests (requires live NocoDB)
├── setup.py                  # Package config
├── features.json             # Feature tracking (37 features)
├── tests.json                # Test specifications (138 test cases)
├── e2e-progress.txt          # E2E test discovery log
├── claude-progress.txt       # Development log
├── MIGRATION.md              # v1 to v3 migration guide
├── PLAN.md                   # Implementation plan
├── contributors.md           # Contributors list
├── init.sh                   # Environment setup script
└── README.md                 # User documentation
```

## Architecture

### Module Structure

- `nocodb/nocodb.py` - Core domain models and abstract interfaces
  - `AuthToken`, `APIToken`, `JWTAuthToken` - Authentication classes
  - `NocoDBBase` - Base identifier (v3 API), replaces `NocoDBProject`
  - `NocoDBClient` - Abstract client interface with method signatures
  - `WhereFilter` - Abstract filter interface

- `nocodb/api.py` - URI builder (`NocoDBAPI`)
  - v3 methods: `get_records_uri()`, `get_record_uri()`, `get_linked_records_uri()`, etc.
  - Deprecated v1 methods: `get_table_uri()`, `get_row_detail_uri()` (emit warnings)

- `nocodb/infra/requests_client.py` - HTTP client implementation (`NocoDBRequestsClient`)
  - v3 Data methods: `records_list_v3()`, `record_get_v3()`, `records_create_v3()`, `attachment_upload_v3()`, `button_action_trigger_v3()`, etc.
  - v3 Meta methods: `tables_list_v3()`, `table_get_v3()`, `fields_list_v3()`, `field_read_v3()`, `base_members_list()`, etc.
  - v2 Meta methods: `bases_list_v3()`, `views_list()`, `view_filters_list()`, `view_sorts_list()`, `webhooks_list()`, etc.
  - Legacy v1 methods: `table_row_list()`, `table_row_create()`, etc. (deprecated)

- `nocodb/filters/` - Query filter system
  - `__init__.py` - Filter classes: `EqFilter`, `LikeFilter`, `IsFilter`, `InFilter`, `BetweenFilter`
  - `logical.py` - Logical operators: `And`, `Or`, `Not` (v3 syntax: `~and`, `~or`)
  - `factory.py` - `basic_filter_class_factory()` for creating custom filters
  - `raw_filter.py` - `RawFilter` for custom filter strings

### v3 API Key Differences

| Aspect | v1 API | v3 API |
|--------|--------|--------|
| Path structure | `/api/v1/db/data/{org}/{project}/{table}` | `/api/v3/data/{baseId}/{tableId}/records` |
| Project concept | `NocoDBProject(org, project_name)` | `NocoDBBase(base_id)` |
| Response format | Flat dict `{Id: 1, Name: "..."}` | Nested `{id: 1, fields: {Name: "..."}}` |
| Batch operations | Single record | Array: `[{id: 1, fields: {...}}]` |
| Filter operators | `ge`, `le` | `gte`, `lte` |

### Not Supported (Enterprise Only)

These features require NocoDB Enterprise and are excluded from this client:
- Workspaces (multi-tenant hierarchy)
- Teams
- Workspace members
- v3 Views API (use v2 instead)
- v3 Bases list (use v2 instead)

## Testing

Tests are colocated with source files using `*_test.py` pattern:
- `nocodb/filters/filters_test.py`
- `nocodb/filters/factory_test.py`
- `nocodb/filters/logical_test.py`
- `nocodb/infra/requests_client_test.py`

## Dependencies

- `requests>=2.0` - HTTP client
- `pytest` - Testing (dev)
