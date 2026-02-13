"""NocoDB CLI package.

The CLI is auto-generated from the MCP server using FastMCP's generate-cli.
Run ./scripts/regenerate-cli.sh after modifying MCP tools.

Structure:
- main.py: Entry point, handles 'init' command, delegates to wrapper
- wrapper.py: Config injection, command aliasing, parameter mapping
- generated.py: Auto-generated CLI with all MCP tools
- config.py: Config file loading (~/.nocodbrc)
"""

from .main import main

__all__ = ["main"]
