"""Attachment commands for NocoDB CLI."""

from pathlib import Path
from typing import Optional
import mimetypes

import typer

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_json,
    print_single_item,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Attachment operations")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("upload")
def upload_attachment(
    ctx: typer.Context,
    table_id: str = typer.Option(..., "--table-id", "-t", help="Table ID"),
    record_id: str = typer.Option(..., "--record-id", "-r", help="Record ID"),
    field_id: str = typer.Option(..., "--field-id", "-f", help="Attachment field ID"),
    file_path: Path = typer.Option(..., "--file", help="Path to file to upload"),
    content_type: Optional[str] = typer.Option(None, "--content-type", "-c", help="MIME type (auto-detected if not provided)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Upload a file attachment to a record field.

    Example:
        nocodb attachments upload -t tbl_xxx -r 1 -f fld_xxx --file ./image.png
    """
    try:
        if not file_path.exists():
            print_error(f"File not found: {file_path}", as_json=output_json)
            raise typer.Exit(1)

        if not file_path.is_file():
            print_error(f"Not a file: {file_path}", as_json=output_json)
            raise typer.Exit(1)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        # Read file content
        content = file_path.read_bytes()
        filename = file_path.name

        # Auto-detect content type if not provided
        if content_type is None:
            detected_type, _ = mimetypes.guess_type(str(file_path))
            content_type = detected_type or "application/octet-stream"

        result = client.attachment_upload_v3(
            base_id,
            table_id,
            record_id,
            field_id,
            filename,
            content,
            content_type,
        )

        if output_json:
            print_json(result)
        else:
            print_success(f"Uploaded {filename} ({content_type})")
            print_single_item(result, title="Attachment")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
