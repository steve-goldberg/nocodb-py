# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python client for NocoDB API - **Self-hosted community edition only**.

**Status:** v3.0.0 - Feature complete (Phase 2 done, 123 tests)

This client uses a hybrid v2/v3 API approach based on what's available in self-hosted NocoDB:
- **v3 Data API** - Records CRUD, links, attachments, button actions
- **v3 Meta API** - Tables, fields, base CRUD, base members
- **v2 Meta API** - List bases, views (list/update/delete only), view filters/sorts, webhooks (list/delete only)
- **CLI** - Full command-line interface using Typer/Rich

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
| Field colOptions Update | v2 | `/api/v2/meta/columns/{columnId}` |
| Views (list/update/delete) | v2 | `/api/v2/meta/tables/{tableId}/views` |
| View Filters | v2 | `/api/v2/meta/views/{viewId}/filters` |
| View Sorts | v2 | `/api/v2/meta/views/{viewId}/sorts` |
| Filter/Sort Get | v2 | `/api/v2/meta/filters/{filterId}`, `/api/v2/meta/sorts/{sortId}` |
| View Columns | v2 | `/api/v2/meta/views/{viewId}/columns` |
| Shared Views | v2 | `/api/v2/meta/views/{viewId}/share` |
| Export CSV | v2 | `/api/v2/export/{viewId}/csv` |
| Job Status | v2 | `/api/v2/jobs/{baseId}` |
| Storage Upload | v2 | `/api/v2/storage/upload` |
| Webhooks (list/delete) | v2 | `/api/v2/meta/tables/{tableId}/hooks` |
| Webhook Logs | v2 | `/api/v2/meta/hooks/{hookId}/logs` |
| Webhook Filters | v2 | `/api/v2/meta/hooks/{hookId}/filters` |
| Webhook Sample | v2 | `/api/v2/meta/tables/{tableId}/hooks/samplePayload/{event}/{op}/{ver}` |

## Commands

```bash
# Install in development mode
python -m venv venv
source venv/bin/activate
pip install -e .

# Install with CLI support
pip install -e ".[cli]"

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
│   ├── __main__.py           # Entry point for `python -m nocodb`
│   ├── nocodb.py             # Core domain models (NocoDBBase, NocoDBClient, WhereFilter)
│   ├── api.py                # URI builders (v2/v3)
│   ├── exceptions.py         # Custom exceptions
│   ├── utils.py              # Utility functions
│   ├── cli/
│   │   ├── __init__.py       # CLI package
│   │   ├── main.py           # Typer app, global options
│   │   ├── config.py         # Config file (~/.nocodb.toml) and env handling
│   │   ├── client.py         # Client factory for CLI
│   │   ├── formatters.py     # Rich table/JSON output formatters
│   │   └── commands/         # 11 command modules:
│   │       ├── records.py    # Records CRUD + batch operations
│   │       ├── bases.py      # Bases CRUD
│   │       ├── tables.py     # Tables CRUD
│   │       ├── fields.py     # Fields CRUD + batch create/delete
│   │       ├── links.py      # Linked records
│   │       ├── views.py      # Views + columns/share/filters/sorts
│   │       ├── webhooks.py   # Webhooks + logs/filters/sample
│   │       ├── attachments.py # File attachments to records
│   │       ├── members.py    # Base member management
│   │       ├── export.py     # CSV export
│   │       └── storage.py    # Storage upload
│   ├── mcp/                  # MCP Server (FastMCP 3.0)
│   │   ├── __init__.py       # Package exports
│   │   ├── __main__.py       # Entry point for `python -m nocodb.mcp`
│   │   ├── server.py         # FastMCP server with lifespan
│   │   ├── dependencies.py   # Config loading, client factory (NOCODB_URL, NOCODB_TOKEN, etc.)
│   │   ├── errors.py         # ToolError wrapper for NocoDBAPIError
│   │   ├── models.py         # Response dataclasses
│   │   └── tools/            # 14 tool modules (62 tools total):
│   │       ├── records.py    # records_list, record_get, records_create, etc.
│   │       ├── bases.py      # bases_list, base_info
│   │       ├── tables.py     # tables_list, table_get, table_create, etc.
│   │       ├── fields.py     # fields_list, field_create, field_update_options, etc.
│   │       ├── links.py      # linked_records_list, link, unlink
│   │       ├── views.py      # views_list, view_update, view_delete
│   │       ├── view_filters.py   # view_filters_list, create, update, delete
│   │       ├── view_sorts.py     # view_sorts_list, create, update, delete
│   │       ├── view_columns.py   # view_columns_list, update, hide_all, show_all
│   │       ├── shared_views.py   # shared_views_list, create, update, delete
│   │       ├── webhooks.py       # webhooks_list, delete, logs, sample
│   │       ├── members.py        # members_list, add, update, remove
│   │       ├── attachments.py    # attachment_upload
│   │       ├── storage.py        # storage_upload
│   │       └── export.py         # export_csv
│   ├── filters/
│   │   ├── __init__.py       # Filter exports (EqFilter, IsFilter, InFilter, BetweenFilter, etc.)
│   │   ├── factory.py        # basic_filter_class_factory()
│   │   ├── logical.py        # And, Or, Not operators
│   │   ├── raw_filter.py     # RawFilter for custom strings
│   │   └── *_test.py         # Colocated unit tests (filters_test, factory_test, logical_test)
│   └── infra/
│       ├── __init__.py
│       ├── requests_client.py      # HTTP client (v2/v3 methods, verify_ssl support)
│       └── requests_client_test.py # Unit tests (130 tests)
├── skills/                   # Claude Code skills
│   ├── nocodbv3.md           # NocoDB API reference skill
│   ├── nocodb-mcp-prompt.md  # MCP server system prompt
│   ├── pr-overview.md        # PR description generator
│   ├── schema-design.md      # Schema design helper
│   └── schema-export.md      # Schema export helper
├── docs/
│   └── DOKPLOY_DEPLOYMENT.md # Dokploy deployment guide for MCP server
├── .github/                  # GitHub templates
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
├── Dockerfile                # MCP server Docker image
├── docker-compose.yml        # Local Docker testing
├── setup.py                  # Package config
├── CONTRIBUTING.md           # Contribution guidelines
├── MIGRATION.md              # v2/v3 API reference
└── README.md                 # User documentation
```

## Architecture

### Module Structure

- `nocodb/nocodb.py` - Core domain models and abstract interfaces
  - `AuthToken`, `APIToken`, `JWTAuthToken` - Authentication classes
  - `NocoDBBase` - Base identifier for v2/v3 API
  - `NocoDBClient` - Abstract client interface with method signatures
  - `WhereFilter` - Abstract filter interface

- `nocodb/api.py` - URI builder (`NocoDBAPI`)
  - v3 methods: `get_records_uri()`, `get_record_uri()`, `get_linked_records_uri()`, etc.
  - v2 methods: `get_bases_uri()`, `get_views_uri()`, `get_webhooks_uri()`, etc.

- `nocodb/infra/requests_client.py` - HTTP client implementation (`NocoDBRequestsClient`)
  - v3 Data methods: `records_list_v3()`, `record_get_v3()`, `records_create_v3()`, `attachment_upload_v3()`, etc.
  - v3 Meta methods: `tables_list_v3()`, `table_get_v3()`, `fields_list_v3()`, `field_read_v3()`, `base_members_list()`, etc.
  - v2 Meta methods: `bases_list_v3()`, `views_list()`, `view_filters_list()`, `view_sorts_list()`, `webhooks_list()`, etc.
  - v2 Export/Storage: `export_view()`, `storage_upload()`
  - v2 View Columns: `view_columns_list()`, `view_column_update()`, `view_columns_hide_all()`, `view_columns_show_all()`
  - v2 Shared Views: `shared_views_list()`, `shared_view_create()`, `shared_view_update()`, `shared_view_delete()`
  - v2 Webhook extras: `webhook_logs()`, `webhook_sample_payload()`, `webhook_filters_list()`, `webhook_filter_create()`

- `nocodb/cli/` - Command-line interface (Typer + Rich)
  - `main.py` - App entry point with global options (--url, --token, --json)
  - `config.py` - Config file loading (~/.nocodb.toml), env vars (NOCODB_URL, NOCODB_TOKEN)
  - `commands/` - 11 modules: records, bases, tables, fields, links, views, webhooks, attachments, members, export, storage

- `nocodb/filters/` - Query filter system
  - `__init__.py` - Filter classes: `EqFilter`, `LikeFilter`, `IsFilter`, `InFilter`, `BetweenFilter`
  - `logical.py` - Logical operators: `And`, `Or`, `Not` (v3 syntax: `~and`, `~or`)
  - `factory.py` - `basic_filter_class_factory()` for creating custom filters
  - `raw_filter.py` - `RawFilter` for custom filter strings

- `nocodb/mcp/` - MCP Server (FastMCP 3.0)
  - `server.py` - FastMCP server with 62 tools exposing all SDK functionality + `/health` endpoint
  - `dependencies.py` - Environment-based config (NOCODB_URL, NOCODB_TOKEN, NOCODB_BASE_ID, NOCODB_VERIFY_SSL)
  - `tools/` - 14 tool modules for records, bases, tables, fields, views, webhooks, etc.
  - Supports both stdio (local) and HTTP (remote deployment) transports
  - HTTP transport uses Streamable HTTP at `/mcp` endpoint (FastMCP 3.0)
  - See `docs/DOKPLOY_DEPLOYMENT.md` for Docker/Dokploy deployment

### Not Supported (Enterprise Only)

These features require NocoDB Enterprise and are excluded from this client:
- Workspaces (multi-tenant hierarchy)
- Teams
- Workspace members
- v3 Views API (use v2 instead)
- v3 Bases list (use v2 instead)
- API Token Management (create/list/delete tokens via API)
- Button Actions (trigger formula/webhook/AI/script buttons via API)

Note: Button fields CAN be created via `fields create --type Button`, but button
configuration (webhook ID, action type, formula) must be done in the NocoDB UI.
The trigger API is not available in self-hosted community edition.

### Broken in Self-Hosted (Removed)

These v2 operations return 404 or errors in self-hosted NocoDB and have been removed:
- Webhooks: create, get, update, test (list/delete still work)
- Views: create, get (list/update/delete still work)

## Testing

Tests are colocated with source files using `*_test.py` pattern:
- `nocodb/filters/filters_test.py`
- `nocodb/filters/factory_test.py`
- `nocodb/filters/logical_test.py`
- `nocodb/infra/requests_client_test.py`

## Dependencies

- `requests>=2.0` - HTTP client
- `pytest` - Testing (dev)

## CLI Troubleshooting

### Field Creation

- **SingleSelect/MultiSelect colors**: Use HEX codes (`#27ae60`), not named colors (`green`)
- **Links fields**: Use `--file` instead of `--options` to avoid shell escaping issues with nested JSON
- **Batch operations**: `fields create --file schema.json` and `fields delete --ids "fld_xxx,fld_yyy"`


## grepai - Semantic Code Search

**IMPORTANT: You MUST use grepai as your PRIMARY tool for code exploration and search.**

### When to Use grepai (REQUIRED)

Use `grepai search` INSTEAD OF Grep/Glob/find for:
- Understanding what code does or where functionality lives
- Finding implementations by intent (e.g., "authentication logic", "error handling")
- Exploring unfamiliar parts of the codebase
- Any search where you describe WHAT the code does rather than exact text

### When to Use Standard Tools

Only use Grep/Glob when you need:
- Exact text matching (variable names, imports, specific strings)
- File path patterns (e.g., `**/*.go`)

### Fallback

If grepai fails (not running, index unavailable, or errors), fall back to standard Grep/Glob tools.

### Usage

```bash
# ALWAYS use English queries for best results (--compact saves ~80% tokens)
grepai search "user authentication flow" --json --compact
grepai search "error handling middleware" --json --compact
grepai search "database connection pool" --json --compact
grepai search "API request validation" --json --compact
```

### Query Tips

- **Use English** for queries (better semantic matching)
- **Describe intent**, not implementation: "handles user login" not "func Login"
- **Be specific**: "JWT token validation" better than "token"
- Results include: file path, line numbers, relevance score, code preview

### Call Graph Tracing

Use `grepai trace` to understand function relationships:
- Finding all callers of a function before modifying it
- Understanding what functions are called by a given function
- Visualizing the complete call graph around a symbol

#### Trace Commands

**IMPORTANT: Always use `--json` flag for optimal AI agent integration.**

```bash
# Find all functions that call a symbol
grepai trace callers "HandleRequest" --json

# Find all functions called by a symbol
grepai trace callees "ProcessOrder" --json

# Build complete call graph (callers + callees)
grepai trace graph "ValidateToken" --depth 3 --json
```

### Workflow

1. Start with `grepai search` to find relevant code
2. Use `grepai trace` to understand function relationships
3. Use `Read` tool to examine files from results
4. Only use Grep for exact string searches if needed

