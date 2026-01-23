"""Button action commands for NocoDB CLI."""

from typing import List

import typer

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_json,
    print_records_table,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Button action operations")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


def _parse_record_ids(record_ids_str: str) -> List[int]:
    """Parse comma-separated record IDs into a list of integers."""
    ids = []
    for part in record_ids_str.split(","):
        part = part.strip()
        if part:
            if part.isdigit():
                ids.append(int(part))
            else:
                ids.append(part)
    return ids


@app.command("trigger")
def trigger_button(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    column_id: str = typer.Option(..., "--column-id", "-c", help="Button column ID"),
    record_ids: str = typer.Option(..., "--record-ids", "-r", help="Comma-separated record IDs (max 25)"),
    preview: bool = typer.Option(False, "--preview", "-p", help="Preview mode (don't execute action)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Trigger a button action on one or more records.

    Supports Formula, Webhook, AI, and Script button types.
    Maximum 25 records per request.

    Example:
        nocodb buttons trigger -t tbl_xxx -c fld_xxx -r 1,2,3
        nocodb buttons trigger -t tbl_xxx -c fld_xxx -r 1 --preview
    """
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        row_ids = _parse_record_ids(record_ids)

        if len(row_ids) == 0:
            print_error("No record IDs provided", as_json=output_json)
            raise typer.Exit(1)

        if len(row_ids) > 25:
            print_error("Maximum 25 records per request", as_json=output_json)
            raise typer.Exit(1)

        result = client.button_action_trigger_v3(
            base_id,
            table_id,
            column_id,
            row_ids,
            preview=preview,
        )

        if output_json:
            print_json(result)
        else:
            mode = "Preview" if preview else "Triggered"
            print_success(f"{mode} button action on {len(row_ids)} record(s)")
            if result:
                records = result if isinstance(result, list) else [result]
                print_records_table(records, title="Updated Records")

    except ValueError as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
