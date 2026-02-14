"""MCP client for connecting to NocoDB MCP server via HTTP streamable transport."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


class MCPClient:
    """Client for NocoDB MCP server using HTTP streamable transport."""

    def __init__(self, url: str):
        """Initialize MCP client.

        Args:
            url: MCP server URL (e.g., http://ncdbmcp.lab/mcp)
        """
        self.url = url
        self._session: ClientSession | None = None
        self._tools: list[dict[str, Any]] = []
        self._resources: dict[str, str] = {}

    async def connect(self) -> None:
        """Connect to the MCP server and discover tools/resources."""
        logger.info(f"Connecting to MCP server at {self.url}...")

        async with streamablehttp_client(self.url) as (read, write, _):
            async with ClientSession(read, write) as session:
                self._session = session
                await session.initialize()

                # Discover tools
                tools_result = await session.list_tools()
                self._tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.inputSchema if hasattr(tool, 'inputSchema') else {},
                        }
                    }
                    for tool in tools_result.tools
                ]
                logger.info(f"Discovered {len(self._tools)} MCP tools")

                # Discover and cache resources
                resources_result = await session.list_resources()
                for resource in resources_result.resources:
                    content = await session.read_resource(resource.uri)
                    if content.contents:
                        self._resources[str(resource.uri)] = content.contents[0].text
                logger.info(f"Cached {len(self._resources)} MCP resources")

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        """Call an MCP tool.

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        async with streamablehttp_client(self.url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)

                # Extract text content from result
                if result.content:
                    texts = [c.text for c in result.content if hasattr(c, 'text')]
                    return "\n".join(texts)
                return ""

    def get_tools_for_llm(self) -> list[dict[str, Any]]:
        """Get tools in OpenAI function-calling format."""
        return self._tools

    def get_resource(self, uri: str) -> str:
        """Get cached resource content.

        Args:
            uri: Resource URI (e.g., nocodb://workflow-guide)

        Returns:
            Resource content as string
        """
        return self._resources.get(uri, "")

    def get_system_prompt(self) -> str:
        """Build system prompt from MCP resources."""
        workflow = self.get_resource("nocodb://workflow-guide")
        reference = self.get_resource("nocodb://reference")

        parts = [
            "You are nocobot, a helpful assistant for working with NocoDB databases.",
            "You have access to NocoDB tools via MCP to help users manage their data.",
            "",
        ]

        if workflow:
            parts.append(workflow)
            parts.append("")

        if reference:
            parts.append(reference)

        return "\n".join(parts)
