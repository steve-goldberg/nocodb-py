"""View management commands for NocoDB CLI."""

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


VIEW_TYPES = {
    "grid": 3,
    "gallery": 1,
    "kanban": 2,
    "calendar": 4,
    "form": 5,
}


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


@app.command("get")
def get_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get view details."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.view_read(view_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title=f"View: {result.get('title', view_id)}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("create")
def create_view(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    title: str = typer.Option(..., "--title", help="View title"),
    view_type: str = typer.Option("grid", "--type", help="View type: grid, gallery, kanban, calendar, form"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a new view."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        type_num = VIEW_TYPES.get(view_type.lower())
        if type_num is None:
            print_error(f"Invalid view type: {view_type}. Must be one of: {', '.join(VIEW_TYPES.keys())}", as_json=output_json)
            raise typer.Exit(1)

        body = {"title": title, "type": type_num}

        result = client.view_create(table_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created view: {result.get('title', 'unknown')}")
            print_single_item(result)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_view(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a view."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {}
        if title:
            body["title"] = title

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.view_update(view_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated view {view_id}")

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
