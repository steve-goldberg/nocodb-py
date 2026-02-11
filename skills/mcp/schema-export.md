# Schema Export Workflow

Export a NocoDB table schema to a portable JSON format for backup or reuse.

## Arguments

| Arg | Required | Description |
|-----|----------|-------------|
| `table_id` | Yes | Table ID to export |
| `output` | No | Output file path (default: stdout) |
| `base_id` | No | Base ID (uses NOCODB_BASE_ID if not set) |

## Usage

```bash
# Export to stdout
python scripts/schema_export.py TABLE_ID

# Export to file with pretty printing
python scripts/schema_export.py TABLE_ID -o schema.json --pretty

# With explicit base ID
python scripts/schema_export.py TABLE_ID -b BASE_ID -o schema.json
```

## Output Format

The exported schema is compatible with `nocodb tables create --fields`:

```json
{
  "title": "MyTable",
  "fields": [
    {"title": "Name", "type": "SingleLineText"},
    {"title": "Email", "type": "Email"},
    {"title": "Status", "type": "SingleSelect", "options": {"choices": [
      {"title": "Active", "color": "#27ae60"},
      {"title": "Inactive", "color": "#e74c3c"}
    ]}}
  ]
}
```

## What Gets Exported

- All user-defined fields with their types and options
- Field titles, types, default values, validation settings

## What Gets Excluded

- System fields (CreatedTime, LastModifiedTime, CreatedBy, LastModifiedBy)
- Auto-increment primary keys
- Internal IDs (fk_model_id, base_id, source_id)
- Timestamps (created_at, updated_at)

## Round-Trip Workflow

```bash
# 1. Export existing table schema
python scripts/schema_export.py tbl_abc123 -o schema.json --pretty

# 2. Modify schema.json as needed (change title, add/remove fields)

# 3. Create new table from schema
nocodb tables create --title "NewTable" --fields "$(cat schema.json | jq -c '.fields')"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `NOCODB_TOKEN` not set | Export token: `export NOCODB_TOKEN=your-token` |
| Table not found | Verify table ID with `nocodb tables list --json` |
| Permission denied | Check API token has read access to the base |
