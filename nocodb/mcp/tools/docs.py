"""Documentation tools for NocoDB MCP server.

Exposes workflow guide and reference docs as tools since mcp-remote
doesn't proxy MCP resources - only tools.

Provides:
- get_workflow_guide: Critical rules for schema discovery
- get_reference: Full reference documentation for all tools
"""

from ..server import mcp
from ..resources import WORKFLOW_CONTENT, REFERENCE_CONTENT


@mcp.tool
def get_workflow_guide() -> str:
    """Get the NocoDB workflow guide - CRITICAL rules for schema discovery.

    READ THIS FIRST before using sort or where parameters!

    The API returns 400 Bad Request if you use field names that don't exist.
    This guide explains the required workflow:
    1. tables_list -> Get table IDs
    2. fields_list(table_id) -> REQUIRED before sort/where
    3. records_list(...) -> Query using actual field names

    Returns:
        Markdown guide with workflow rules, examples, and troubleshooting.
    """
    return WORKFLOW_CONTENT


@mcp.tool
def get_reference() -> str:
    """Get the complete NocoDB MCP reference documentation.

    Contains:
    - All 60 tool descriptions organized by category
    - Field type reference with options examples
    - Filter syntax guide
    - Common workflow examples
    - Self-hosted limitations
    - Destructive operation requirements

    Returns:
        Full markdown reference documentation.
    """
    return REFERENCE_CONTENT
