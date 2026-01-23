"""Storage commands for NocoDB CLI."""

from pathlib import Path
from typing import Optional
import mimetypes

import typer

from nocodb.cli.client import create_client
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_json,
    print_single_item,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Storage operations (general file upload)")


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("upload")
def upload_file(
    ctx: typer.Context,
    file_path: Path = typer.Argument(..., help="Path to file to upload"),
    content_type: Optional[str] = typer.Option(None, "--content-type", "-c", help="MIME type (auto-detected if not provided)"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Upload a file to NocoDB storage.

    This uploads a file to general storage, not attached to any record.
    Use 'attachments upload' to attach files to specific records.

    Examples:
        nocodb storage upload ./document.pdf
        nocodb storage upload ./image.png --content-type image/png
        nocodb storage upload ./data.json --json
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

        # Read file content
        content = file_path.read_bytes()
        filename = file_path.name

        # Auto-detect content type if not provided
        if content_type is None:
            detected_type, _ = mimetypes.guess_type(str(file_path))
            content_type = detected_type or "application/octet-stream"

        result = client.storage_upload(
            filename,
            content,
            content_type,
        )

        if output_json:
            print_json(result)
        else:
            print_success(f"Uploaded {filename} ({content_type})")
            # SDK returns a list of uploaded files, extract first item for display
            display_item = result[0] if isinstance(result, list) and result else result
            print_single_item(display_item, title="Storage File")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
