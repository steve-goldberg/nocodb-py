"""Main CLI entry point for NocoDB.

This module provides the entry point for the `nocodb` command.
It delegates to the wrapper module which:
1. Loads config from ~/.nocodbrc and environment variables
2. Transforms commands to the generated CLI format
3. Runs the generated CLI

The generated CLI (generated.py) is auto-generated from the MCP server.
Run ./scripts/regenerate-cli.sh after modifying MCP tools.
"""

import sys
from pathlib import Path

from .config import create_example_config


def init_config(path: Path, force: bool = False) -> int:
    """Create example configuration file.

    This is the only command handled directly - all others go through
    the generated CLI.
    """
    if path.exists() and not force:
        print(f"Error: Config file already exists at {path}. Use --force to overwrite.")
        return 1

    path.write_text(create_example_config())
    print(f"Created config file at {path}")
    print("\nEdit the file and set your NocoDB URL.")
    print("For security, set your token via NOCODB_TOKEN environment variable.")
    return 0


def main() -> int:
    """Main entry point for the nocodb CLI."""
    args = sys.argv[1:]

    # Handle init command directly (not an MCP tool)
    if args and args[0] == "init":
        # Handle help for init
        if "--help" in args or "-h" in args:
            print("Usage: nocodb init [OPTIONS]")
            print("\nCreate example configuration file.\n")
            print("Options:")
            print("  --path, -p PATH  Config file path (default: ~/.nocodbrc)")
            print("  --force, -f      Overwrite existing config")
            return 0

        path = Path.home() / ".nocodbrc"
        force = False

        i = 1
        while i < len(args):
            if args[i] in ("--path", "-p") and i + 1 < len(args):
                path = Path(args[i + 1])
                i += 2
            elif args[i] in ("--force", "-f"):
                force = True
                i += 1
            else:
                i += 1

        return init_config(path, force)

    # All other commands go through the wrapper
    from .wrapper import run_wrapped_cli
    return run_wrapped_cli(args)


if __name__ == "__main__":
    sys.exit(main())
