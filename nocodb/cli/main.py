"""Main CLI application for NocoDB."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from nocodb import __version__

from .config import Config, create_example_config, load_config
from .formatters import print_error

app = typer.Typer(
    name="nocodb",
    help="NocoDB CLI - Agent-friendly command-line interface for NocoDB API",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

_config: Optional[Config] = None


def get_config() -> Config:
    """Get the current configuration."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    url: Optional[str] = typer.Option(
        None, "--url", "-u", envvar="NOCODB_URL", help="NocoDB instance URL"
    ),
    token: Optional[str] = typer.Option(
        None, "--token", envvar="NOCODB_TOKEN", help="API token"
    ),
    base_id: Optional[str] = typer.Option(
        None, "--base-id", "-b", envvar="NOCODB_BASE_ID", help="Default base ID"
    ),
    profile: Optional[str] = typer.Option(
        None, "--profile", "-p", envvar="NOCODB_PROFILE", help="Config profile to use"
    ),
    config_file: Optional[Path] = typer.Option(
        None, "--config", "-c", envvar="NOCODB_CONFIG", help="Config file path"
    ),
    version: bool = typer.Option(
        False, "--version", "-V", help="Show version and exit"
    ),
) -> None:
    """NocoDB CLI - Agent-friendly command-line interface."""
    if version:
        console.print(f"nocodb-cli version {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()

    global _config
    _config = load_config(
        url=url,
        token=token,
        base_id=base_id,
        profile=profile,
        config_path=config_file,
    )

    ctx.ensure_object(dict)
    ctx.obj["config"] = _config


@app.command("init")
def init_config(
    path: Path = typer.Option(
        Path.home() / ".nocodbrc",
        "--path",
        "-p",
        help="Config file path",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing config"
    ),
) -> None:
    """Create example configuration file."""
    if path.exists() and not force:
        print_error(f"Config file already exists at {path}. Use --force to overwrite.")
        raise typer.Exit(1)

    path.write_text(create_example_config())
    console.print(f"[green]Created config file at {path}[/green]")
    console.print("\nEdit the file and set your NocoDB URL.")
    console.print("For security, set your token via NOCODB_TOKEN environment variable.")


from .commands import attachments, bases, fields, links, members, records, tables, views, webhooks

app.add_typer(records.app, name="records", help="Record operations")
app.add_typer(bases.app, name="bases", help="Base management")
app.add_typer(tables.app, name="tables", help="Table management")
app.add_typer(fields.app, name="fields", help="Field management")
app.add_typer(links.app, name="links", help="Linked records operations")
app.add_typer(views.app, name="views", help="View management")
app.add_typer(webhooks.app, name="webhooks", help="Webhook management")
app.add_typer(attachments.app, name="attachments", help="Attachment operations")
app.add_typer(members.app, name="members", help="Base member management")


@app.command("list")
def list_resource(
    ctx: typer.Context,
    resource: str = typer.Argument(..., help="Resource type: bases, tables, records, fields, views, webhooks"),
    table_id: Optional[str] = typer.Option(None, "--table-id", "-t", help="Table ID"),
    view_id: Optional[str] = typer.Option(None, "--view-id", "-v", help="View ID"),
    filter_str: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter expression"),
    sort: Optional[str] = typer.Option(None, "--sort", "-s", help="Sort field (prefix with - for desc)"),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(25, "--page-size", "-n", help="Results per page"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List resources (shortcut for `nocodb <resource> list`)."""
    config = ctx.obj.get("config") if ctx.obj else get_config()

    if resource == "bases":
        bases.list_bases(ctx, output_json=output_json)
    elif resource == "tables":
        tables.list_tables(ctx, output_json=output_json)
    elif resource == "records":
        if not table_id:
            print_error("--table-id is required for listing records", as_json=output_json)
            raise typer.Exit(1)
        records.list_records(
            ctx,
            table_id=table_id,
            filter_str=filter_str,
            sort=sort,
            page=page,
            page_size=page_size,
            output_json=output_json,
        )
    elif resource == "fields":
        if not table_id:
            print_error("--table-id is required for listing fields", as_json=output_json)
            raise typer.Exit(1)
        fields.list_fields(ctx, table_id=table_id, output_json=output_json)
    elif resource == "views":
        if not table_id:
            print_error("--table-id is required for listing views", as_json=output_json)
            raise typer.Exit(1)
        views.list_views(ctx, table_id=table_id, output_json=output_json)
    elif resource == "webhooks":
        if not table_id:
            print_error("--table-id is required for listing webhooks", as_json=output_json)
            raise typer.Exit(1)
        webhooks.list_webhooks(ctx, table_id=table_id, output_json=output_json)
    else:
        print_error(f"Unknown resource: {resource}", as_json=output_json)
        raise typer.Exit(1)


@app.command("get")
def get_resource(
    ctx: typer.Context,
    resource: str = typer.Argument(..., help="Resource type: base, table, record, field, view, webhook"),
    resource_id: str = typer.Argument(..., help="Resource ID"),
    table_id: Optional[str] = typer.Option(None, "--table-id", "-t", help="Table ID (for records)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Get a single resource (shortcut for `nocodb <resource> get`)."""
    config = ctx.obj.get("config") if ctx.obj else get_config()

    if resource == "base":
        bases.get_base(ctx, base_id=resource_id, output_json=output_json)
    elif resource == "table":
        tables.get_table(ctx, table_id=resource_id, output_json=output_json)
    elif resource == "record":
        if not table_id:
            print_error("--table-id is required for getting a record", as_json=output_json)
            raise typer.Exit(1)
        records.get_record(ctx, table_id=table_id, record_id=resource_id, output_json=output_json)
    elif resource == "field":
        fields.get_field(ctx, field_id=resource_id, output_json=output_json)
    elif resource == "view":
        views.get_view(ctx, view_id=resource_id, output_json=output_json)
    elif resource == "webhook":
        webhooks.get_webhook(ctx, hook_id=resource_id, output_json=output_json)
    else:
        print_error(f"Unknown resource: {resource}", as_json=output_json)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
