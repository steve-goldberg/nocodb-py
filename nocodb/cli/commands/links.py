"""Linked records commands for NocoDB CLI."""

from typing import Optional

import typer

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_json,
    print_records_table,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Linked records operations")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_links(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    link_field_id: str = typer.Option(..., "--link-field", "-l", help="Link field ID"),
    record_id: str = typer.Option(..., "--record-id", "-r", help="Source record ID"),
    fields_list: Optional[str] = typer.Option(None, "--fields", help="Comma-separated field names to return"),
    sort: Optional[str] = typer.Option(None, "--sort", "-s", help="Sort field (prefix with - for desc)"),
    filter_str: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter expression: (field,op,value)"),
    page: int = typer.Option(1, "--page", help="Page number"),
    page_size: int = typer.Option(25, "--page-size", "-n", help="Results per page"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List linked records.

    Examples:
        nocodb links list -t tbl_xxx -l fld_xxx -r 1
        nocodb links list -t tbl_xxx -l fld_xxx -r 1 --fields Name,Status --sort -Created
        nocodb links list -t tbl_xxx -l fld_xxx -r 1 --filter "(Status,eq,Active)"
    """
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        params = {"page": page, "pageSize": page_size}
        if fields_list:
            params["fields"] = fields_list
        if sort:
            params["sort"] = sort
        if filter_str:
            params["where"] = filter_str

        result = client.linked_records_list_v3(
            base_id, table_id, link_field_id, record_id, params=params
        )

        records = result.get("list", result.get("records", []))

        if output_json:
            print_json(result, meta={"page": page, "pageSize": page_size})
        else:
            field_names = fields_list.split(",") if fields_list else None
            print_records_table(
                records,
                title=f"Linked Records (Record #{record_id}, Field {link_field_id})",
                fields=field_names
            )

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("link")
def link_records(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    link_field_id: str = typer.Option(..., "--link-field", "-l", help="Link field ID"),
    record_id: str = typer.Option(..., "--record-id", "-r", help="Source record ID"),
    targets: str = typer.Option(..., "--targets", help="Target record IDs (comma-separated)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Link records together."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        target_ids = [int(t.strip()) if t.strip().isdigit() else t.strip() for t in targets.split(",")]

        result = client.linked_records_link_v3(
            base_id, table_id, link_field_id, record_id, target_ids
        )

        if output_json:
            print_json(result or {"linked": target_ids})
        else:
            print_success(f"Linked {len(target_ids)} record(s) to record #{record_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("unlink")
def unlink_records(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    link_field_id: str = typer.Option(..., "--link-field", "-l", help="Link field ID"),
    record_id: str = typer.Option(..., "--record-id", "-r", help="Source record ID"),
    targets: str = typer.Option(..., "--targets", help="Target record IDs (comma-separated)"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Unlink records."""
    try:
        target_ids = [int(t.strip()) if t.strip().isdigit() else t.strip() for t in targets.split(",")]

        if not force and not output_json:
            confirm = typer.confirm(f"Unlink {len(target_ids)} record(s) from record #{record_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.linked_records_unlink_v3(
            base_id, table_id, link_field_id, record_id, target_ids
        )

        if output_json:
            print_json(result or {"unlinked": target_ids})
        else:
            print_success(f"Unlinked {len(target_ids)} record(s) from record #{record_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
