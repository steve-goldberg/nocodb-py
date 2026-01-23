"""Export commands for NocoDB CLI."""

from pathlib import Path
from typing import Optional

import typer

from nocodb.cli.client import create_client
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Export view data to CSV")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("csv")
def export_csv(
    ctx: typer.Context,
    view_id: str = typer.Argument(..., help="View ID to export"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Row offset for pagination"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Maximum rows to export"),
) -> None:
    """Export view data as CSV.

    Examples:
        nocodb export csv vw_xxx                      # Print to stdout
        nocodb export csv vw_xxx -o data.csv          # Save to file
        nocodb export csv vw_xxx --limit 100          # Export first 100 rows
        nocodb export csv vw_xxx --offset 50 --limit 50  # Export rows 51-100
    """
    try:
        config = _get_config(ctx)
        client = create_client(config)

        csv_content = client.export_view(
            view_id,
            offset=offset,
            limit=limit,
        )

        if output:
            output.write_bytes(csv_content)
            print_success(f"Exported to {output}")
        else:
            # Print to stdout
            print(csv_content.decode("utf-8"), end="")

    except Exception as e:
        print_error(str(e))
        raise typer.Exit(1)


# Also register the csv command as the default when just running `nocodb export VIEW_ID`
@app.callback(invoke_without_command=True)
def export_default(
    ctx: typer.Context,
    view_id: Optional[str] = typer.Argument(None, help="View ID to export"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
    offset: Optional[int] = typer.Option(None, "--offset", help="Row offset"),
    limit: Optional[int] = typer.Option(None, "--limit", help="Maximum rows"),
) -> None:
    """Export view data as CSV (default format).

    Examples:
        nocodb export vw_xxx                  # Print to stdout
        nocodb export vw_xxx -o data.csv      # Save to file
    """
    if ctx.invoked_subcommand is None and view_id:
        # Direct invocation without subcommand - use csv export
        export_csv(ctx, view_id, output, offset, limit)
