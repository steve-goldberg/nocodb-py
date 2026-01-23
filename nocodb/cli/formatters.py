"""Output formatters for NocoDB CLI."""

import json
from typing import Any, Optional

from rich.console import Console
from rich.table import Table

console = Console()
error_console = Console(stderr=True)


def format_json(data: Any, meta: Optional[dict] = None) -> str:
    """Format data as JSON string."""
    output = {"success": True, "data": data}
    if meta:
        output["meta"] = meta
    return json.dumps(output, indent=2, default=str)


def format_error_json(message: str, code: Optional[int] = None) -> str:
    """Format error as JSON string."""
    error = {"message": message}
    if code:
        error["code"] = code
    return json.dumps({"success": False, "error": error}, indent=2)


def print_json(data: Any, meta: Optional[dict] = None) -> None:
    """Print data as JSON."""
    console.print(format_json(data, meta))


def print_error(message: str, code: Optional[int] = None, as_json: bool = False) -> None:
    """Print error message."""
    if as_json:
        error_console.print(format_error_json(message, code))
    else:
        prefix = f"[HTTP {code}] " if code else ""
        error_console.print(f"[red]Error: {prefix}{message}[/red]")


def print_success(message: str, as_json: bool = False) -> None:
    """Print success message."""
    if as_json:
        console.print(json.dumps({"success": True, "message": message}))
    else:
        console.print(f"[green]{message}[/green]")


def create_table(title: str, columns: list[str]) -> Table:
    """Create a Rich table with given columns."""
    table = Table(title=title, show_header=True, header_style="bold cyan")
    for col in columns:
        table.add_column(col)
    return table


def print_records_table(
    records: list[dict],
    title: str = "Records",
    fields: Optional[list[str]] = None,
) -> None:
    """Print records as a formatted table."""
    if not records:
        console.print("[yellow]No records found[/yellow]")
        return

    first_record = records[0]
    record_fields = first_record.get("fields", first_record)

    if fields:
        columns = ["ID"] + fields
    else:
        columns = ["ID"] + list(record_fields.keys())[:6]

    table = create_table(title, columns)

    for record in records:
        record_id = str(record.get("id", record.get("Id", "")))
        record_fields = record.get("fields", record)

        row = [record_id]
        for col in columns[1:]:
            value = record_fields.get(col, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value, default=str)
            row.append(str(value)[:50])
        table.add_row(*row)

    console.print(table)


def print_items_table(
    items: list[dict],
    title: str,
    columns: list[tuple[str, str]],
) -> None:
    """Print items as a formatted table.

    Args:
        items: List of dictionaries to display
        title: Table title
        columns: List of (key, display_name) tuples
    """
    if not items:
        console.print(f"[yellow]No {title.lower()} found[/yellow]")
        return

    table = create_table(title, [col[1] for col in columns])

    for item in items:
        row = []
        for key, _ in columns:
            value = item.get(key, "")
            if isinstance(value, (list, dict)):
                value = json.dumps(value, default=str)
            row.append(str(value)[:50] if value else "")
        table.add_row(*row)

    console.print(table)


def print_single_item(item: dict, title: str = "Details") -> None:
    """Print a single item's details."""
    console.print(f"\n[bold cyan]{title}[/bold cyan]")
    for key, value in item.items():
        if isinstance(value, (list, dict)):
            value = json.dumps(value, indent=2, default=str)
        console.print(f"  [bold]{key}:[/bold] {value}")
    console.print()
