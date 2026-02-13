"""CLI wrapper for NocoDB generated CLI.

Provides:
1. Config injection - loads from ~/.nocodbrc and environment variables
2. Command aliases - maps familiar commands to generated tool calls
3. Parameter mapping - translates CLI flags to tool parameters
"""

import os
import sys
from pathlib import Path
from typing import Optional

from .config import load_config

# Command alias mapping: (group, command) -> tool_name
COMMAND_ALIASES = {
    # Records
    ("records", "list"): "records_list",
    ("records", "list-all"): "records_list_all",
    ("records", "get"): "record_get",
    ("records", "create"): "records_create",
    ("records", "update"): "records_update",
    ("records", "delete"): "records_delete",
    ("records", "count"): "records_count",
    # Bases
    ("bases", "list"): "bases_list",
    ("bases", "info"): "base_info",
    # Tables
    ("tables", "list"): "tables_list",
    ("tables", "get"): "table_get",
    ("tables", "create"): "table_create",
    ("tables", "update"): "table_update",
    ("tables", "delete"): "table_delete",
    # Fields
    ("fields", "list"): "fields_list",
    ("fields", "get"): "field_get",
    ("fields", "create"): "field_create",
    ("fields", "update"): "field_update",
    ("fields", "update-options"): "field_update_options",
    ("fields", "delete"): "field_delete",
    # Links
    ("links", "list"): "linked_records_list",
    ("links", "link"): "linked_records_link",
    ("links", "unlink"): "linked_records_unlink",
    # Views
    ("views", "list"): "views_list",
    ("views", "update"): "view_update",
    ("views", "delete"): "view_delete",
    # View filters
    ("filters", "list"): "view_filters_list",
    ("filters", "get"): "view_filter_get",
    ("filters", "create"): "view_filter_create",
    ("filters", "update"): "view_filter_update",
    ("filters", "delete"): "view_filter_delete",
    ("filters", "children"): "view_filter_children",
    # View sorts
    ("sorts", "list"): "view_sorts_list",
    ("sorts", "get"): "view_sort_get",
    ("sorts", "create"): "view_sort_create",
    ("sorts", "update"): "view_sort_update",
    ("sorts", "delete"): "view_sort_delete",
    # View columns
    ("columns", "list"): "view_columns_list",
    ("columns", "update"): "view_column_update",
    ("columns", "hide-all"): "view_columns_hide_all",
    ("columns", "show-all"): "view_columns_show_all",
    # Shared views
    ("shared", "list"): "shared_views_list",
    ("shared", "create"): "shared_view_create",
    ("shared", "update"): "shared_view_update",
    ("shared", "delete"): "shared_view_delete",
    # Webhooks
    ("webhooks", "list"): "webhooks_list",
    ("webhooks", "delete"): "webhook_delete",
    ("webhooks", "logs"): "webhook_logs",
    ("webhooks", "sample"): "webhook_sample_payload",
    ("webhooks", "filters"): "webhook_filters_list",
    ("webhooks", "filter-create"): "webhook_filter_create",
    # Members
    ("members", "list"): "members_list",
    ("members", "add"): "member_add",
    ("members", "update"): "member_update",
    ("members", "remove"): "member_remove",
    # Attachments
    ("attachments", "upload"): "attachment_upload",
    # Storage
    ("storage", "upload"): "storage_upload",
    # Export
    ("export", "csv"): "export_csv",
    # Schema
    ("schema", "table"): "schema_export_table",
    ("schema", "base"): "schema_export_base",
}

# Parameter alias mapping: --kebab-case -> --snake_case for generated CLI
PARAM_ALIASES = {
    "--table-id": "--table_id",
    "--record-id": "--record_id",
    "--field-id": "--field_id",
    "--view-id": "--view_id",
    "--hook-id": "--hook_id",
    "--filter-id": "--filter_id",
    "--sort-id": "--sort_id",
    "--member-id": "--member_id",
    "--link-field-id": "--link_field_id",
    "--page-size": "--page_size",
    "--max-pages": "--max_pages",
    "--field-type": "--field_type",
    "--fk-column-id": "--fk_column_id",
    "--comparison-op": "--comparison_op",
    "--col-options": "--col_options",
    "--column-id": "--column_id",
    "--target-ids": "--target_ids",
    "--record-ids": "--record_ids",
    "--content-base64": "--content_base64",
    "--content-type": "--content_type",
    "--filter-group-id": "--filter_group_id",
    # Short flags
    "-t": "--table_id",
    "-f": "--filter",  # For filter strings (not --force)
    "-s": "--sort",
    "-n": "--page_size",
    "-v": "--view_id",
}


def inject_config_to_env(
    url: Optional[str] = None,
    token: Optional[str] = None,
    base_id: Optional[str] = None,
    profile: Optional[str] = None,
    config_path: Optional[Path] = None,
) -> None:
    """Load config and inject into environment for the generated CLI.

    The generated CLI connects to the MCP server, which reads these env vars.
    """
    config = load_config(
        url=url,
        token=token,
        base_id=base_id,
        profile=profile,
        config_path=config_path,
    )

    # Only set if not already set (CLI flags override env)
    if config.url and not os.environ.get("NOCODB_URL"):
        os.environ["NOCODB_URL"] = config.url
    if config.token and not os.environ.get("NOCODB_TOKEN"):
        os.environ["NOCODB_TOKEN"] = config.token
    if config.base_id and not os.environ.get("NOCODB_BASE_ID"):
        os.environ["NOCODB_BASE_ID"] = config.base_id


def transform_args(args: list[str]) -> list[str]:
    """Transform CLI args to match generated CLI format.

    Transforms:
    - nocodb records list -> nocodb call-tool records_list
    - --table-id -> --table_id
    - --force -> --confirm (for destructive operations)
    """
    if not args:
        return args

    # Handle shortcut commands: "list bases" -> "bases list"
    if args[0] == "list" and len(args) > 1:
        resource = args[1]
        return transform_args([resource, "list"] + args[2:])
    elif args[0] == "get" and len(args) > 1:
        resource = args[1]
        return transform_args([resource, "get"] + args[2:])

    # Check for command alias
    if len(args) >= 2:
        group, cmd = args[0], args[1]
        tool_name = COMMAND_ALIASES.get((group, cmd))
        if tool_name:
            # Transform to: call-tool <tool_name> <remaining_args>
            remaining = args[2:]
            transformed = ["call-tool", tool_name] + transform_params(remaining)
            return transformed

    # Not a known command, pass through with param transformation
    return transform_params(args)


def transform_params(args: list[str]) -> list[str]:
    """Transform parameter names and handle special flags."""
    result = []
    i = 0
    while i < len(args):
        arg = args[i]

        # Handle --force/-f for destructive operations
        if arg in ("--force", "-f"):
            # Only transform to --confirm if this looks like a destructive command
            # (has --confirm parameter in the tool). We'll add --confirm true
            result.append("--confirm")
            result.append("true")
            i += 1
            continue

        # Handle parameter aliases
        if arg in PARAM_ALIASES:
            result.append(PARAM_ALIASES[arg])
        else:
            result.append(arg)
        i += 1

    return result


def run_wrapped_cli(args: Optional[list[str]] = None) -> int:
    """Run the generated CLI with config injection and argument transformation."""
    if args is None:
        args = sys.argv[1:]

    # Extract global options before transformation
    url = None
    token = None
    base_id = None
    profile = None
    config_path = None

    filtered_args = []
    i = 0
    while i < len(args):
        arg = args[i]

        if arg in ("--url", "-u") and i + 1 < len(args):
            url = args[i + 1]
            i += 2
            continue
        elif arg in ("--token",) and i + 1 < len(args):
            token = args[i + 1]
            i += 2
            continue
        elif arg in ("--base-id", "-b") and i + 1 < len(args):
            base_id = args[i + 1]
            i += 2
            continue
        elif arg in ("--profile", "-p") and i + 1 < len(args):
            profile = args[i + 1]
            i += 2
            continue
        elif arg in ("--config", "-c") and i + 1 < len(args):
            config_path = Path(args[i + 1])
            i += 2
            continue
        elif arg in ("--version", "-V"):
            from nocodb import __version__
            print(f"nocodb-cli version {__version__}")
            return 0

        filtered_args.append(arg)
        i += 1

    # Inject config into environment
    inject_config_to_env(url, token, base_id, profile, config_path)

    # Transform args
    transformed = transform_args(filtered_args)

    # Import and run the generated CLI
    from .generated import app

    # cyclopts uses sys.argv, so we need to update it
    sys.argv = ["nocodb"] + transformed

    try:
        app()
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0
