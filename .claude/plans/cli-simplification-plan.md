# Plan: CLI Simplification - Agent-Friendly UX Improvements

## Mode: NEW_FEATURE

## Research Summary

### Files Involved
- [nocodb/cli/main.py](nocodb/cli/main.py) - Main app, global options, shortcut commands
- [nocodb/cli/commands/records.py](nocodb/cli/commands/records.py) - Record CRUD (most used)
- [nocodb/cli/commands/fields.py](nocodb/cli/commands/fields.py) - Field management
- [nocodb/cli/commands/links.py](nocodb/cli/commands/links.py) - Link operations (verbose)
- [nocodb/cli/commands/views.py](nocodb/cli/commands/views.py) - View management (702 lines!)
- [nocodb/cli/formatters.py](nocodb/cli/formatters.py) - Output formatting
- [nocodb/cli/skill.md](nocodb/cli/skill.md) - Agent documentation

### Current Pain Points Identified

1. **Records create/update requires JSON** - `--data '{"Name": "Test"}'` is error-prone
2. **Links commands are extremely verbose** - `-t TABLE -l LINK_FIELD -r RECORD --targets IDS`
3. **Filter syntax is unintuitive** - `--filter "(Status,eq,Active)~and(Priority,gt,5)"`
4. **No positional shortcuts** for common operations
5. **Inconsistent argument patterns** between commands

### Comparison with agent-browser CLI

agent-browser excels at:
- Simple verb-first commands: `click @e2`, `fill @e3 "text"`
- Refs for element targeting: `@e2` instead of complex selectors
- Minimal JSON requirements
- Natural action words

## Target State

A CLI that:
1. Works without JSON for simple cases
2. Supports key=value syntax for record operations
3. Has simpler filter syntax (`--where Status=Active`)
4. Reduces flag noise for common operations
5. Maintains full power for complex cases via existing syntax

## Implementation Steps

### Phase 1: Key-Value Record Operations (HIGH IMPACT)

#### Step 1.1: Add key=value support to `records create`
- File: [nocodb/cli/commands/records.py](nocodb/cli/commands/records.py)
- Action: Modify `create_record()` to accept positional args as key=value pairs
- Details:
  ```bash
  # NEW: Key-value syntax (no JSON needed)
  nocodb records create -t TABLE_ID Name="Test" Status="Active"

  # STILL WORKS: JSON for complex values
  nocodb records create -t TABLE_ID --data '{"Nested": {"key": "val"}}'
  ```

#### Step 1.2: Add key=value support to `records update`
- File: [nocodb/cli/commands/records.py](nocodb/cli/commands/records.py)
- Action: Modify `update_record()` to accept positional args
- Details:
  ```bash
  # NEW: Simple update
  nocodb records update -t TABLE_ID 1 Status="Done"

  # STILL WORKS: JSON for complex updates
  nocodb records update -t TABLE_ID 1 --data '{"Nested": {...}}'
  ```

### Phase 2: Simplified Filter Syntax (MEDIUM IMPACT)

#### Step 2.1: Add `--where` flag with simpler syntax
- File: [nocodb/cli/commands/records.py](nocodb/cli/commands/records.py)
- Action: Add `--where` flag that converts simple syntax to NocoDB filter format
- Details:
  ```bash
  # NEW: Simple operators
  nocodb records list -t TABLE_ID --where Status=Active
  nocodb records list -t TABLE_ID --where "Priority>5"
  nocodb records list -t TABLE_ID --where Status=Active --where "Priority>5"

  # Operators: = != > >= < <= ~ !~ (for like/nlike)

  # STILL WORKS: Full filter syntax for complex cases
  nocodb records list -t TABLE_ID --filter "(Status,in,Active,Pending)"
  ```

#### Step 2.2: Create filter parser utility
- File: NEW [nocodb/cli/filters.py](nocodb/cli/filters.py)
- Action: Create parser to convert simple syntax to NocoDB format
- Details:
  ```python
  def parse_simple_where(where_clauses: list[str]) -> str:
      """Convert ['Status=Active', 'Priority>5'] to '(Status,eq,Active)~and(Priority,gt,5)'"""
  ```

### Phase 3: Link Commands Simplification (MEDIUM IMPACT)

#### Step 3.1: Add positional syntax for links
- File: [nocodb/cli/commands/links.py](nocodb/cli/commands/links.py)
- Action: Allow positional args to reduce flag noise
- Details:
  ```bash
  # CURRENT (verbose)
  nocodb links link -t TABLE_ID -l LINK_FIELD_ID -r RECORD_ID --targets "22,43"

  # NEW: Positional (table, record, field, targets all positional)
  nocodb links add TABLE_ID RECORD_ID LINK_FIELD 22,43

  # Also add aliases
  nocodb link TABLE_ID RECORD_ID LINK_FIELD 22,43  # shortcut
  ```

#### Step 3.2: Add `link` and `unlink` as top-level commands
- File: [nocodb/cli/main.py](nocodb/cli/main.py)
- Action: Register shortcut commands at app level
- Details:
  ```bash
  nocodb link TABLE_ID RECORD_ID FIELD_ID 22,43
  nocodb unlink TABLE_ID RECORD_ID FIELD_ID 22 -f
  ```

### Phase 4: Field Creation Shortcuts (LOWER IMPACT)

#### Step 4.1: Add colon syntax for field types
- File: [nocodb/cli/commands/fields.py](nocodb/cli/commands/fields.py)
- Action: Support `Name:Type` positional syntax
- Details:
  ```bash
  # NEW: Colon syntax
  nocodb fields add -t TABLE_ID Email:Email
  nocodb fields add -t TABLE_ID "Status:SingleSelect" Active,Pending,Done

  # STILL WORKS: Full options
  nocodb fields create -t TABLE_ID --title Email --type Email
  ```

### Phase 5: Natural Language Aliases (LOWER IMPACT)

#### Step 5.1: Add intuitive command aliases
- File: [nocodb/cli/main.py](nocodb/cli/main.py)
- Action: Register aliases for common operations
- Details:
  ```bash
  nocodb find -t TABLE Status=Active   # alias for records list --where
  nocodb count -t TABLE                 # alias for records count
  nocodb schema TABLE_ID                # alias for fields list
  nocodb show table TABLE_ID            # alias for tables get
  ```

### Phase 6: Update Documentation

#### Step 6.1: Update skill.md with new syntax
- File: [nocodb/cli/skill.md](nocodb/cli/skill.md)
- Action: Add "Quick Syntax" section at top, document all new patterns

## Testing Plan

- [ ] Key-value syntax parses correctly for simple cases
- [ ] Key-value syntax handles quoted values with spaces
- [ ] `--where` converts to valid NocoDB filter syntax
- [ ] Multiple `--where` flags combine with AND
- [ ] Positional link commands work
- [ ] All existing JSON/flag syntax still works (backwards compatible)
- [ ] Error messages are helpful when syntax is wrong

## Risk Assessment

1. **Backwards Compatibility** - All existing commands MUST continue working
   - Mitigation: New syntax is additive, tests verify old syntax

2. **Ambiguous Parsing** - Key=value could conflict with other args
   - Mitigation: Use Typer's Argument with nargs=-1, careful parsing

3. **Filter Edge Cases** - Simple syntax may not cover all operators
   - Mitigation: Keep `--filter` for complex cases, document limitations

## Implementation Order

Priority by impact-to-effort ratio:

1. **Phase 1** - Key-value records (highest impact, moderate effort)
2. **Phase 2** - Simple filters (high impact, low effort)
3. **Phase 3** - Link simplification (medium impact, low effort)
4. **Phase 5** - Aliases (medium impact, very low effort)
5. **Phase 4** - Field shortcuts (lower impact, moderate effort)
6. **Phase 6** - Documentation (required, low effort)

## Questions for User

1. Should key=value be the **default** syntax (with --data as fallback) or optional alongside --data?
2. For `--where`, should multiple clauses default to AND or support explicit AND/OR?
3. Do you want the positional link syntax to replace flags entirely, or just be an alternative?
4. Any specific command patterns you find most painful that I should prioritize?

---

## Summary of New Commands After Implementation

```bash
# Records (key-value syntax)
nocodb records create -t TABLE Name="John" Email="john@test.com"
nocodb records update -t TABLE 1 Status="Done"

# Filtering (simple syntax)
nocodb records list -t TABLE --where Status=Active --where "Priority>5"

# Links (positional)
nocodb link TABLE RECORD FIELD 22,43
nocodb unlink TABLE RECORD FIELD 22 -f

# Aliases
nocodb find -t TABLE Status=Active
nocodb count -t TABLE
nocodb schema TABLE

# Fields (colon syntax)
nocodb fields add -t TABLE Email:Email
```

All existing verbose syntax continues to work for complex cases and backwards compatibility.
