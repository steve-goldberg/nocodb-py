#!/usr/bin/env python3
"""Export complete NocoDB base schema to portable JSON format.

Usage:
    python scripts/export_base_schema.py [--base-id BASE_ID] [--output FILE] [--pretty]

Exports base metadata and all tables with their portable schemas.
Output format suitable for recreating the base structure.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import load_config
from schema_utils import extract_portable_base_schema


def export_base(base_id: str, client) -> dict:
    """Export complete base schema using SDK.

    1. Fetch base metadata via base_read()
    2. List all tables via tables_list_v3()
    3. For each table, fetch full schema via table_read_v3()
    4. Transform to portable format
    """
    # Get base metadata
    base_data = client.base_read(base_id)

    # Get list of all tables
    tables_response = client.tables_list_v3(base_id)
    tables_list = tables_response.get("list", [])

    # Fetch full schema for each table
    tables_data = []
    for table in tables_list:
        table_id = table["id"]
        table_data = client.table_read_v3(base_id, table_id)
        tables_data.append(table_data)

    # Convert to portable format
    return extract_portable_base_schema(base_data, tables_data)


def main():
    parser = argparse.ArgumentParser(
        description="Export NocoDB base schema to portable JSON"
    )
    parser.add_argument(
        "--base-id", "-b",
        help="Base ID (uses config default if not specified)",
    )
    parser.add_argument(
        "--profile", "-p",
        default="default",
        help="Config profile name",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file (default: stdout)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output",
    )

    args = parser.parse_args()

    try:
        # Load config with profile support
        config = load_config(
            base_id=args.base_id,
            profile=args.profile,
        )

        # Create SDK client
        client = create_client(config)

        # Get base_id (from args or config)
        base_id = get_base_id(config, args.base_id)

        # Export schema
        schema = export_base(base_id, client)

        # Format output
        indent = 2 if args.pretty else None
        output = json.dumps(schema, indent=indent)

        # Write output
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
                f.write("\n")
            print(f"Base schema exported to {args.output}", file=sys.stderr)
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
