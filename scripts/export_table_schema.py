#!/usr/bin/env python3
"""Export NocoDB table schema to portable JSON format.

Usage:
    python scripts/export_table_schema.py TABLE_ID [--output FILE] [--base-id BASE_ID]

Output format compatible with `nocodb tables create --fields`.
Uses SDK directly instead of CLI subprocess for better performance.
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for imports when running as script
sys.path.insert(0, str(Path(__file__).parent.parent))

from nocodb.cli.client import create_client, get_base_id
from nocodb.cli.config import load_config
from schema_utils import extract_portable_table_schema


def main():
    parser = argparse.ArgumentParser(
        description="Export NocoDB table schema to portable JSON"
    )
    parser.add_argument(
        "table_id",
        help="Table ID to export",
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

        # Fetch table metadata directly via SDK
        table_data = client.table_read_v3(base_id, args.table_id)

        # Convert to portable format
        schema = extract_portable_table_schema(table_data)

        # Format output
        indent = 2 if args.pretty else None
        output = json.dumps(schema, indent=indent)

        # Write output
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
                f.write("\n")
            print(f"Schema exported to {args.output}", file=sys.stderr)
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
