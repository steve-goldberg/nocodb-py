"""Base member commands for NocoDB CLI."""

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import Config
from nocodb.cli.formatters import (
    print_error,
    print_json,
    print_single_item,
    print_success,
)

app = typer.Typer(no_args_is_help=True, help="Base member management")
console = Console()

# Valid roles for base members
VALID_ROLES = ["owner", "creator", "editor", "commenter", "viewer"]


def _get_config(ctx: typer.Context) -> Config:
    """Get config from context."""
    if ctx.obj and "config" in ctx.obj:
        return ctx.obj["config"]
    from nocodb.cli.config import load_config
    return load_config()


@app.command("list")
def list_members(
    ctx: typer.Context,
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """List all members of the current base."""
    try:
        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.base_members_list(base_id)
        members = result.get("members", result.get("list", []))

        if output_json:
            print_json(result)
        else:
            if not members:
                console.print("[dim]No members found[/dim]")
                return

            table = Table(title=f"Base Members (Base: {base_id})")
            table.add_column("ID", style="cyan")
            table.add_column("Email", style="white")
            table.add_column("Role", style="green")
            table.add_column("Created", style="dim")

            for member in members:
                member_id = str(member.get("id", ""))
                email = member.get("email", "")
                roles = member.get("roles", "")
                created = member.get("created_at", "")[:10] if member.get("created_at") else ""

                table.add_row(member_id, email, roles, created)

            console.print(table)

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("add")
def add_member(
    ctx: typer.Context,
    email: str = typer.Option(..., "--email", "-e", help="User email address"),
    role: str = typer.Option("viewer", "--role", "-r", help=f"Member role: {', '.join(VALID_ROLES)}"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Add a member to the current base.

    Example:
        nocodb members add -e user@example.com -r editor
        nocodb members add --email user@example.com --role viewer
    """
    try:
        if role not in VALID_ROLES:
            print_error(f"Invalid role: {role}. Must be one of: {', '.join(VALID_ROLES)}", as_json=output_json)
            raise typer.Exit(1)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.base_member_add(base_id, {"email": email, "roles": role})

        if output_json:
            print_json(result)
        else:
            print_success(f"Added {email} as {role}")
            print_single_item(result, title="Member")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("update")
def update_member(
    ctx: typer.Context,
    member_id: str = typer.Argument(..., help="Member ID to update"),
    role: str = typer.Option(..., "--role", "-r", help=f"New role: {', '.join(VALID_ROLES)}"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Update a member's role.

    Example:
        nocodb members update usr_xxx -r editor
        nocodb members update usr_xxx --role commenter
    """
    try:
        if role not in VALID_ROLES:
            print_error(f"Invalid role: {role}. Must be one of: {', '.join(VALID_ROLES)}", as_json=output_json)
            raise typer.Exit(1)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.base_member_update(base_id, member_id, {"roles": role})

        if output_json:
            print_json(result)
        else:
            print_success(f"Updated member {member_id} to role: {role}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)


@app.command("remove")
def remove_member(
    ctx: typer.Context,
    member_id: str = typer.Argument(..., help="Member ID to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
    output_json: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
) -> None:
    """Remove a member from the base.

    Example:
        nocodb members remove usr_xxx
        nocodb members remove usr_xxx --force
    """
    try:
        if not force and not output_json:
            confirm = typer.confirm(f"Remove member {member_id}?")
            if not confirm:
                print_error("Cancelled", as_json=output_json)
                raise typer.Exit(0)

        config = _get_config(ctx)
        client = create_client(config)
        base_id = get_base_id(config)

        result = client.base_member_remove(base_id, member_id)

        if output_json:
            print_json({"removed": member_id, "success": True})
        else:
            print_success(f"Removed member {member_id}")

    except Exception as e:
        print_error(str(e), as_json=output_json)
        raise typer.Exit(1)
