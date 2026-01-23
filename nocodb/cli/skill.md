# NocoDB CLI Skill

Agent-friendly command-line interface for NocoDB API (self-hosted community edition).

## Quick Setup

```bash
# Install with CLI extras
pip install nocodb[cli]

# Create config file
nocodb init

# Set token (recommended: use env var)
export NOCODB_TOKEN="your-api-token"
export NOCODB_URL="http://localhost:8080"
export NOCODB_BASE_ID="your-default-base-id"
```

## Command Structure

```
nocodb [VERB] [RESOURCE] [ID] [--flags]
```

**Verbs:** list, get, create, update, delete, count, link, unlink, test

## Universal Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--json` | `-j` | Machine-readable JSON output |
| `--base-id` | `-b` | Base ID (or from config/env) |
| `--table-id` | `-t` | Table ID |
| `--force` | `-f` | Skip confirmation prompts |

## Records

```bash
# List records with filtering and sorting
nocodb records list -t TABLE_ID [--filter "(Status,eq,Active)"] [--sort "-Created"] [--json]

# Get single record
nocodb records get -t TABLE_ID RECORD_ID [--json]

# Create record
nocodb records create -t TABLE_ID --data '{"Name": "Test", "Status": "Active"}' [--json]

# Update record
nocodb records update -t TABLE_ID RECORD_ID --data '{"Status": "Done"}' [--json]

# Delete record
nocodb records delete -t TABLE_ID RECORD_ID [-f] [--json]

# Count records
nocodb records count -t TABLE_ID [--filter "(Status,eq,Active)"] [--json]
```

### Filter Syntax

Format: `(field,operator,value)`

| Operator | Example | Description |
|----------|---------|-------------|
| `eq` | `(Status,eq,Active)` | Equal |
| `neq` | `(Status,neq,Done)` | Not equal |
| `gt` | `(Age,gt,18)` | Greater than |
| `gte` | `(Age,gte,18)` | Greater than or equal |
| `lt` | `(Age,lt,65)` | Less than |
| `lte` | `(Age,lte,65)` | Less than or equal |
| `like` | `(Name,like,%test%)` | Contains |
| `nlike` | `(Name,nlike,%spam%)` | Does not contain |
| `is` | `(Status,is,null)` | Null check: `null`, `notnull`, `empty`, `notempty` |
| `in` | `(Tags,in,a,b,c)` | Match any in list |
| `btw` | `(Age,btw,18,65)` | Between range |

Combine with `~and`, `~or`, `~not`:
```bash
--filter "(Status,eq,Active)~and(Priority,gt,5)"
--filter "(Status,eq,Open)~or(Status,eq,Pending)"
--filter "~not(Status,eq,Archived)"
```

## Bases

```bash
nocodb bases list [--json]
nocodb bases get BASE_ID [--json]
nocodb bases create --title "My Base" [--json]
nocodb bases update BASE_ID --title "New Name" [--json]
nocodb bases delete BASE_ID [-f]
```

## Tables

```bash
nocodb tables list [--json]
nocodb tables get TABLE_ID [--json]
nocodb tables create --title "My Table" [--json]
nocodb tables update TABLE_ID --title "New Name" [--json]
nocodb tables delete TABLE_ID [-f]
```

## Fields

```bash
nocodb fields list -t TABLE_ID [--json]
nocodb fields get FIELD_ID [--json]
nocodb fields create -t TABLE_ID --title "Email" --type Email [--json]
nocodb fields update FIELD_ID --title "New Name" [--json]
nocodb fields delete FIELD_ID [-f]
```

**Field Types:** SingleLineText, LongText, Number, Decimal, Currency, Percent, Email, URL, PhoneNumber, Date, DateTime, Time, Duration, Checkbox, SingleSelect, MultiSelect, Rating, Attachment, Links, Lookup, Rollup, Formula, CreatedTime, LastModifiedTime, CreatedBy, LastModifiedBy

## Linked Records

```bash
# List linked records
nocodb links list -t TABLE_ID -l LINK_FIELD_ID -r RECORD_ID [--json]

# Link records
nocodb links link -t TABLE_ID -l LINK_FIELD_ID -r RECORD_ID --targets "22,43" [--json]

# Unlink records
nocodb links unlink -t TABLE_ID -l LINK_FIELD_ID -r RECORD_ID --targets "22" [-f] [--json]
```

## Views

```bash
nocodb views list -t TABLE_ID [--json]
nocodb views get VIEW_ID [--json]
nocodb views update VIEW_ID --title "New Name" [--json]
nocodb views delete VIEW_ID [-f]

# View filters
nocodb views filters list -v VIEW_ID [--json]
nocodb views filters get FILTER_ID [--json]
nocodb views filters create -v VIEW_ID --column FIELD_ID --op eq --value "test" [--json]
nocodb views filters delete FILTER_ID [-f]
nocodb views filters children FILTER_GROUP_ID [--json]

# View sorts
nocodb views sorts list -v VIEW_ID [--json]
nocodb views sorts get SORT_ID [--json]
nocodb views sorts create -v VIEW_ID --column FIELD_ID --direction asc [--json]
nocodb views sorts delete SORT_ID [-f]

# View columns (visibility per view)
nocodb views columns list VIEW_ID [--json]
nocodb views columns update VIEW_ID COLUMN_ID [--show/--hide] [--order N] [--json]
nocodb views columns hide-all VIEW_ID [--json]
nocodb views columns show-all VIEW_ID [--json]

# Shared views (public links)
nocodb views share list -t TABLE_ID [--json]
nocodb views share create VIEW_ID [--password SECRET] [--json]
nocodb views share update VIEW_ID [--password SECRET] [--json]
nocodb views share delete VIEW_ID [-f] [--json]
```

**View Types:** grid, gallery, kanban, calendar, form

**Note:** View create is not available via API in self-hosted community edition. Use the NocoDB UI to create views.

## Webhooks

```bash
nocodb webhooks list -t TABLE_ID [--json]
nocodb webhooks delete HOOK_ID [-f] [--json]

# Webhook logs
nocodb webhooks logs HOOK_ID [--json]

# Webhook sample payload (preview what webhook will send)
nocodb webhooks sample -t TABLE_ID [--event records] [--operation insert|update|delete] [--version v2] [--json]

# Webhook filters
nocodb webhooks filters list HOOK_ID [--json]
nocodb webhooks filters create HOOK_ID --column FIELD_ID --op eq --value "test" [--json]
```

**Events:** after.insert, after.update, after.delete, after.bulkInsert, after.bulkUpdate, after.bulkDelete

**Note:** Webhook create, get, update, and test are not available via API in self-hosted community edition. Use the NocoDB UI to create/manage webhooks.

## Members

```bash
# List base members
nocodb members list [--json]

# Invite member to base
nocodb members invite EMAIL [--role owner|creator|editor|commenter|viewer] [--json]

# Update member role
nocodb members update USER_ID --role editor [--json]

# Remove member from base
nocodb members remove USER_ID [-f] [--json]
```

**Roles:** owner, creator, editor, commenter, viewer

## Export

```bash
# Export view data as CSV
nocodb export VIEW_ID [--output FILE] [--offset N] [--limit N]
nocodb export csv VIEW_ID [--output FILE] [--offset N] [--limit N]

# Examples
nocodb export vw_xxx                      # Print to stdout
nocodb export vw_xxx -o data.csv          # Save to file
nocodb export vw_xxx --limit 100          # Export first 100 rows
nocodb export vw_xxx --offset 50 --limit 50  # Export rows 51-100
```

## Storage

```bash
# Upload file to NocoDB storage (not attached to any record)
nocodb storage upload FILE [--content-type MIME] [--json]

# Examples
nocodb storage upload ./document.pdf
nocodb storage upload ./image.png --content-type image/png
nocodb storage upload ./data.json --json
```

**Note:** For attaching files to specific records, use `nocodb attachments upload` instead.

## Attachments

```bash
# Upload file and attach to a record field
nocodb attachments upload -t TABLE_ID -r RECORD_ID -f FIELD_ID FILE [--json]

# Examples
nocodb attachments upload -t tbl_xxx -r rec_xxx -f fld_xxx ./photo.jpg
```

## Shortcut Commands

```bash
# Shortcut for listing any resource
nocodb list bases [--json]
nocodb list tables [--json]
nocodb list records -t TABLE_ID [--json]
nocodb list fields -t TABLE_ID [--json]
nocodb list views -t TABLE_ID [--json]
nocodb list webhooks -t TABLE_ID [--json]

# Shortcut for getting any resource
nocodb get base BASE_ID [--json]
nocodb get table TABLE_ID [--json]
nocodb get record RECORD_ID -t TABLE_ID [--json]
nocodb get field FIELD_ID [--json]
nocodb get view VIEW_ID [--json]
nocodb get webhook HOOK_ID [--json]
```

## Configuration

### Config File (`~/.nocodbrc`)

```toml
[default]
url = "http://localhost:8080"
# token should be in NOCODB_TOKEN env var for security
base_id = "your-default-base-id"

[profiles.prod]
url = "https://nocodb.example.com"
base_id = "prod_base_id"

[profiles.dev]
url = "http://localhost:8080"
base_id = "dev_base_id"
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `NOCODB_TOKEN` | API token (required) |
| `NOCODB_URL` | NocoDB instance URL |
| `NOCODB_BASE_ID` | Default base ID |
| `NOCODB_PROFILE` | Config profile to use |
| `NOCODB_CONFIG` | Config file path |

### Priority (highest to lowest)

1. Command-line flags (`--url`, `--token`)
2. Environment variables
3. Profile from config file (if `--profile` set)
4. Default section from config file

## JSON Output Format

All commands support `--json` for machine-readable output:

```json
{
  "success": true,
  "data": { ... },
  "meta": { "page": 1, "pageSize": 25 }
}
```

Error format:
```json
{
  "success": false,
  "error": { "message": "Error description", "code": 404 }
}
```

## Common Workflows

### Create a record and link it

```bash
# Create a project
nocodb records create -t projects --data '{"Name": "New Project"}' --json

# Link to a team
nocodb links link -t projects -l team_link_field -r PROJECT_ID --targets "TEAM_ID"
```

### Filter and export records

```bash
# Get all active high-priority tasks as JSON
nocodb records list -t tasks --filter "(Status,eq,Active)~and(Priority,gte,8)" --json > tasks.json
```

### Batch operations via scripting

```bash
# Delete multiple records
for id in 1 2 3 4 5; do
  nocodb records delete -t TABLE_ID $id -f --json
done
```
