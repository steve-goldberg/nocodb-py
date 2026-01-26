"""View management commands for NocoDB CLI.

Note: View creation is not supported via the v2 API in self-hosted NocoDB.
Use list, update, delete operations for views created through the UI.
Filters and sorts have full CRUD support.
"""

import json
from typing import Optional

import typer

from nocodb.cli.client import create_client
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_items_table,
    print_json,
    print_single_item,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="View management")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_views(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all views for a table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.views_list(table_id)

        views = result.get("list", result.get("views", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("title", "Title"),
                ("type", "Type"),
                ("is_default", "Default"),
            ]
            print_items_table(views, title="Views", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    icon: Optional[str] = typer.Option(None, "--icon", help="View icon (emoji)"),
    meta_json: Optional[str] = typer.Option(None, "--meta", "-m", help="Meta as JSON"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a view.

    Examples:
        nocodb views update vw_xxx --title "New Name"
        nocodb views update vw_xxx --icon "📊"
        nocodb views update vw_xxx --meta '{"icon": "📊"}'
    """
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {}
        if title:
            body["title"] = title

        # Handle icon and meta
        if icon or meta_json:
            meta = {}
            if meta_json:
                try:
                    meta = json.loads(meta_json)
                except json.JSONDecodeError as e:
                    print_error(f"Invalid JSON for --meta: {e}", as_json=output_json)
                    raise typer.Exit(1)
            if icon:
                meta["icon"] = icon
            body["meta"] = meta

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.view_update(view_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated view {view_id}")

    except json.JSONDecodeError:
        raise  # Already handled above
    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("delete")
def delete_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a view."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete view {view_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_delete(view_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted view {view_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


# View Filters subcommands
filters_app = typer.Typer(no_args_is_help=True, help="View filter operations")
app.add_typer(filters_app, name="filters")


@filters_app.command("list")
def list_filters(
    ctx: typer.Context,
    view_id: str = typer.Option(..., "--view-id", "-v", help="View ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List view filters."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_filters_list(view_id)

        filters = result.get("list", result.get("filters", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("fk_column_id", "Column"),
                ("comparison_op", "Operator"),
                ("value", "Value"),
            ]
            print_items_table(filters, title="Filters", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@filters_app.command("create")
def create_filter(
    ctx: typer.Context,
    view_id: str = typer.Option(..., "--view-id", "-v", help="View ID"),
    column_id: str = typer.Option(..., "--column", "-c", help="Column/field ID"),
    operator: str = typer.Option(..., "--op", "-o", help="Comparison operator (eq, neq, like, etc.)"),
    value: str = typer.Option(..., "--value", help="Filter value"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a view filter."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {
            "fk_column_id": column_id,
            "comparison_op": operator,
            "value": value,
        }

        result = client.view_filter_create(view_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created filter on view {view_id}")
            print_single_item(result)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@filters_app.command("update")
def update_filter(
    ctx: typer.Context,
    filter_id: str = typer.Argument(..., help="Filter ID"),
    operator: Optional[str] = typer.Option(None, "--op", "-o", help="Comparison operator (eq, neq, like, etc.)"),
    value: Optional[str] = typer.Option(None, "--value", help="Filter value"),
    column_id: Optional[str] = typer.Option(None, "--column", "-c", help="Column/field ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a view filter."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {}
        if operator:
            body["comparison_op"] = operator
        if value is not None:
            body["value"] = value
        if column_id:
            body["fk_column_id"] = column_id

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.view_filter_update(filter_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated filter {filter_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@filters_app.command("delete")
def delete_filter(
    ctx: typer.Context,
    filter_id: str = typer.Argument(..., help="Filter ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a view filter."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete filter {filter_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_filter_delete(filter_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted filter {filter_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


# View Sorts subcommands
sorts_app = typer.Typer(no_args_is_help=True, help="View sort operations")
app.add_typer(sorts_app, name="sorts")


@sorts_app.command("list")
def list_sorts(
    ctx: typer.Context,
    view_id: str = typer.Option(..., "--view-id", "-v", help="View ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List view sorts."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_sorts_list(view_id)

        sorts = result.get("list", result.get("sorts", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("fk_column_id", "Column"),
                ("direction", "Direction"),
            ]
            print_items_table(sorts, title="Sorts", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@sorts_app.command("create")
def create_sort(
    ctx: typer.Context,
    view_id: str = typer.Option(..., "--view-id", "-v", help="View ID"),
    column_id: str = typer.Option(..., "--column", "-c", help="Column/field ID"),
    direction: str = typer.Option("asc", "--direction", "-d", help="Sort direction: asc or desc"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a view sort."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {
            "fk_column_id": column_id,
            "direction": direction,
        }

        result = client.view_sort_create(view_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created sort on view {view_id}")
            print_single_item(result)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@sorts_app.command("update")
def update_sort(
    ctx: typer.Context,
    sort_id: str = typer.Argument(..., help="Sort ID"),
    direction: Optional[str] = typer.Option(None, "--direction", "-d", help="Sort direction: asc or desc"),
    column_id: Optional[str] = typer.Option(None, "--column", "-c", help="Column/field ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a view sort."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {}
        if direction:
            body["direction"] = direction
        if column_id:
            body["fk_column_id"] = column_id

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.view_sort_update(sort_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated sort {sort_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@sorts_app.command("delete")
def delete_sort(
    ctx: typer.Context,
    sort_id: str = typer.Argument(..., help="Sort ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a view sort."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete sort {sort_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_sort_delete(sort_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted sort {sort_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@sorts_app.command("get")
def get_sort(
    ctx: typer.Context,
    sort_id: str = typer.Argument(..., help="Sort ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get a single sort's details."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_sort_get(sort_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title="Sort")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@filters_app.command("get")
def get_filter(
    ctx: typer.Context,
    filter_id: str = typer.Argument(..., help="Filter ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get a single filter's details."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_filter_get(filter_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title="Filter")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@filters_app.command("children")
def list_filter_children(
    ctx: typer.Context,
    filter_group_id: str = typer.Argument(..., help="Filter group ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List children of a filter group (nested filters)."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_filter_children(filter_group_id)

        filters = result.get("list", result.get("children", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("fk_column_id", "Column"),
                ("comparison_op", "Operator"),
                ("value", "Value"),
            ]
            print_items_table(filters, title="Filter Children", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


# View Columns subcommands
columns_app = typer.Typer(no_args_is_help=True, help="View column visibility operations")
app.add_typer(columns_app, name="columns")


@columns_app.command("list")
def list_view_columns(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List view columns with visibility settings."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_columns_list(view_id)

        columns_list = result.get("list", result.get("columns", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("fk_column_id", "Column ID"),
                ("show", "Visible"),
                ("order", "Order"),
            ]
            print_items_table(columns_list, title="View Columns", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@columns_app.command("update")
def update_view_column(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    column_id: str = typer.Argument(..., help="View column ID"),
    show: Optional[bool] = typer.Option(None, "--show/--hide", help="Show or hide the column"),
    order: Optional[int] = typer.Option(None, "--order", "-o", help="Column order position"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a view column's visibility or order."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {}
        if show is not None:
            body["show"] = show
        if order is not None:
            body["order"] = order

        if not body:
            print_error("No update fields provided. Use --show/--hide or --order", as_json=output_json)
            raise typer.Exit(1)

        result = client.view_column_update(view_id, column_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated column {column_id} in view {view_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@columns_app.command("hide-all")
def hide_all_columns(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Hide all columns in a view."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_columns_hide_all(view_id)

        if output_json:
            print_json(result or {"success": True})
        else:
            print_success(f"Hidden all columns in view {view_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@columns_app.command("show-all")
def show_all_columns(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Show all columns in a view."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_columns_show_all(view_id)

        if output_json:
            print_json(result or {"success": True})
        else:
            print_success(f"Showing all columns in view {view_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


# Shared Views subcommands
share_app = typer.Typer(no_args_is_help=True, help="Shared view (public link) operations")
app.add_typer(share_app, name="share")


@share_app.command("list")
def list_shared_views(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all shared views for a table."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.shared_views_list(table_id)

        shares = result.get("list", result.get("sharedViews", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("fk_view_id", "View ID"),
                ("uuid", "UUID"),
                ("password", "Password"),
            ]
            print_items_table(shares, title="Shared Views", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@share_app.command("create")
def create_shared_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Password protect the share"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a public share link for a view."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.shared_view_create(view_id, password=password)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created shared view for {view_id}")
            print_single_item(result, title="Shared View")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@share_app.command("update")
def update_shared_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="New password (empty to remove)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a shared view's password."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.shared_view_update(view_id, password=password)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated shared view for {view_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@share_app.command("delete")
def delete_shared_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a shared view link."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete shared view for {view_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)

        result = client.shared_view_delete(view_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted shared view for {view_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
