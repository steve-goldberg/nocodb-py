"""Base management commands for NocoDB CLI."""

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

app = typer.Typer(no_args_is_help=True, help="Base management")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_bases(
    ctx: typer.Context,
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all bases."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.bases_list()

        bases = result.get("list", result.get("bases", []))

        if output_json:
            print_json(result)
        else:
            columns = [
                ("id", "ID"),
                ("title", "Title"),
                ("type", "Type"),
                ("created_at", "Created"),
            ]
            print_items_table(bases, title="Bases", columns=columns)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("get")
def get_base(
    ctx: typer.Context,
    base_id: str = typer.Argument(..., help="Base ID"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get base details."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        result = client.base_read(base_id)

        if output_json:
            print_json(result)
        else:
            print_single_item(result, title=f"Base: {result.get('title', base_id)}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("create")
def create_base(
    ctx: typer.Context,
    title: str = typer.Option(..., "--title", help="Base title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="Base description"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Create a new base."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {"title": title}
        if description:
            body["description"] = description

        result = client.base_create(body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Created base: {result.get('title', 'unknown')}")
            print_single_item(result)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_base(
    ctx: typer.Context,
    base_id: str = typer.Argument(..., help="Base ID"),
    title: Optional[str] = typer.Option(None, "--title", help="New title"),
    description: Optional[str] = typer.Option(None, "--description", "-d", help="New description"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a base."""
    try:
        config = _get_config(ctx)
        client = create_client(config)

        body = {}
        if title:
            body["title"] = title
        if description:
            body["description"] = description

        if not body:
            print_error("No update fields provided", as_json=output_json)
            raise typer.Exit(1)

        result = client.base_update(base_id, body)

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated base {base_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("delete")
def delete_base(
    ctx: typer.Context,
    base_id: str = typer.Argument(..., help="Base ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Delete a base."""
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Delete base {base_id}? This cannot be undone.")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)

        result = client.base_delete(base_id)

        if output_json:
            print_json(result or {"deleted": True})
        else:
            print_success(f"Deleted base {base_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
