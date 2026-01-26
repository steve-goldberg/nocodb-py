# Plan: CLI Icon/Meta Support for Tables and Views

## Mode: NEW_FEATURE

## Summary

The SDK already supports setting `meta` (including `icon`) for tables and views via the `body` dict parameter. The CLI commands only expose `--title`. This plan adds `--icon` and `--meta` flags.

## Current State

**SDK (works):**
```python
client.table_update_v3(base_id, table_id, {"meta": {"icon": "🎯"}})
client.view_update(view_id, {"meta": {"icon": "📊"}})
```

**CLI (missing):**
```bash
nocodb tables update TABLE_ID --title "New"  # only --title
nocodb views update VIEW_ID --title "New"    # only --title
```

## Target State

```bash
# Tables
nocodb tables update TABLE_ID --icon "🎯"
nocodb tables update TABLE_ID --meta '{"icon": "🎯", "custom": "value"}'
nocodb tables update TABLE_ID --title "New" --icon "📁"

# Views
nocodb views update VIEW_ID --icon "📊"
nocodb views update VIEW_ID --meta '{"icon": "📊"}'
nocodb views update VIEW_ID --title "Kanban" --icon "📊"
```

## Implementation Steps

### Step 1: Update `tables update` command

**File:** `nocodb/cli/commands/tables.py:117-145`

**Changes:**
```python
@app.command("update")
def update_table(
    ctx: typer.Context,
    table_id: str = typer.Argument(..., help="Table ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    icon: Optional[str] = typer.Option(None, "--icon", help="Table icon (emoji)"),
    meta_json: Optional[str] = typer.Option(None, "--meta", "-m", help="Meta as JSON"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a table."""
    # ... existing code ...

    body = {}
    if title:
        body["title"] = title

    # NEW: Handle icon and meta
    if icon or meta_json:
        meta = {}
        if meta_json:
            meta = json.loads(meta_json)
        if icon:
            meta["icon"] = icon
        body["meta"] = meta

    # ... rest of function ...
```

### Step 2: Update `views update` command

**File:** `nocodb/cli/commands/views.py:64-95`

**Changes:**
```python
@app.command("update")
def update_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    icon: Optional[str] = typer.Option(None, "--icon", help="View icon (emoji)"),
    meta_json: Optional[str] = typer.Option(None, "--meta", "-m", help="Meta as JSON"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a view."""
    # ... existing code ...

    body = {}
    if title:
        body["title"] = title

    # NEW: Handle icon and meta
    if icon or meta_json:
        meta = {}
        if meta_json:
            meta = json.loads(meta_json)
        if icon:
            meta["icon"] = icon
        body["meta"] = meta

    # ... rest of function ...
```

### Step 3: Update CLI skill documentation

**File:** `nocodb/cli/skill.md`

**Add to Tables section:**
```markdown
## Tables

```bash
nocodb tables update TABLE_ID --title "New Name"     # Rename
nocodb tables update TABLE_ID --icon "🎯"            # Set icon
nocodb tables update TABLE_ID --meta '{"icon":"🎯"}' # Set meta JSON
```

**Add to Views section:**
```markdown
## Views

```bash
nocodb views update VIEW_ID --title "New Name"       # Rename
nocodb views update VIEW_ID --icon "📊"              # Set icon
nocodb views update VIEW_ID --meta '{"icon":"📊"}'   # Set meta JSON
```

### Step 4: Update nocodbv3.md skill

**File:** `skills/nocodbv3.md`

Add same examples to the Tables and Views sections.

## Testing Plan

- [ ] `nocodb tables update TABLE_ID --icon "🎯"` sets icon correctly
- [ ] `nocodb tables update TABLE_ID --meta '{"icon":"🎯"}'` sets meta correctly
- [ ] `nocodb tables update TABLE_ID --title "X" --icon "🎯"` sets both
- [ ] `nocodb views update VIEW_ID --icon "📊"` sets icon correctly
- [ ] `nocodb views update VIEW_ID --meta '{"icon":"📊"}'` sets meta correctly
- [ ] `--help` shows new options for both commands
- [ ] Invalid JSON for `--meta` shows helpful error

## Files to Modify

1. `nocodb/cli/commands/tables.py` - Add `--icon` and `--meta` options
2. `nocodb/cli/commands/views.py` - Add `--icon` and `--meta` options
3. `nocodb/cli/skill.md` - Document new options
4. `skills/nocodbv3.md` - Document new options

## Risk Assessment

**Low risk** - Additive change, no breaking changes to existing behavior.
