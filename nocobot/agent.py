"""Agent loop for nocobot - processes messages and calls MCP tools."""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger

from nocobot.bus.events import InboundMessage, OutboundMessage
from nocobot.bus.queue import MessageBus
from nocobot.mcp_client import MCPClient
from nocobot.providers import LiteLLMProvider, ToolCallRequest


class AgentLoop:
    """Agent that processes messages using LLM and MCP tools."""

    def __init__(
        self,
        bus: MessageBus,
        mcp: MCPClient,
        api_key: str,
        model: str = "anthropic/claude-sonnet-4",
        max_iterations: int = 20,
    ):
        """Initialize the agent.

        Args:
            bus: Message bus for receiving/sending messages
            mcp: MCP client for tool calls
            api_key: OpenRouter API key
            model: LLM model to use
            max_iterations: Max tool call iterations per message
        """
        self.bus = bus
        self.mcp = mcp
        self.max_iterations = max_iterations
        self._running = False

        # In-memory conversation history per chat_id
        self._history: dict[str, list[dict[str, Any]]] = {}

        # LLM provider (OpenRouter)
        self._llm = LiteLLMProvider(
            api_key=api_key,
            default_model=model,
            provider_name="openrouter",
        )

        # System prompt (built from MCP resources)
        self._system_prompt = ""

    async def start(self) -> None:
        """Start the agent loop."""
        self._running = True
        self._system_prompt = self.mcp.get_system_prompt()
        logger.info("Agent loop started")

        while self._running:
            try:
                # Wait for inbound message
                msg = await asyncio.wait_for(
                    self.bus.consume_inbound(),
                    timeout=1.0
                )
                await self._process_message(msg)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Agent error: {e}")

    async def stop(self) -> None:
        """Stop the agent loop."""
        self._running = False
        logger.info("Agent loop stopped")

    async def _process_message(self, msg: InboundMessage) -> None:
        """Process an inbound message."""
        logger.debug(f"Processing message from {msg.sender_id}: {msg.content[:50]}...")

        # Handle /new command - clear history
        if msg.content.strip() == "/new":
            self._history.pop(msg.session_key, None)
            await self._send_response(msg, "Conversation cleared. Starting fresh!")
            return

        # Handle /help command
        if msg.content.strip() == "/help":
            help_text = (
                "I'm nocobot, your NocoDB assistant.\n\n"
                "I can help you:\n"
                "- List tables and fields\n"
                "- Query and filter records\n"
                "- Create, update, and delete data\n"
                "- Manage views, filters, and sorts\n\n"
                "Commands:\n"
                "/new - Start a new conversation\n"
                "/help - Show this help message\n\n"
                "Just tell me what you want to do with your NocoDB data!"
            )
            await self._send_response(msg, help_text)
            return

        # Get or create conversation history
        history = self._history.setdefault(msg.session_key, [])

        # Add user message to history
        history.append({"role": "user", "content": msg.content})

        # Build messages for LLM
        messages = [{"role": "system", "content": self._system_prompt}] + history

        # Get MCP tools
        tools = self.mcp.get_tools_for_llm()

        # Agent loop - call LLM, execute tools, repeat
        for iteration in range(self.max_iterations):
            response = await self._llm.chat(
                messages=messages,
                tools=tools if tools else None,
                max_tokens=4096,
                temperature=0.7,
            )

            # If no tool calls, we're done
            if not response.has_tool_calls:
                if response.content:
                    history.append({"role": "assistant", "content": response.content})
                    await self._send_response(msg, response.content)
                return

            # Execute tool calls
            assistant_msg: dict[str, Any] = {"role": "assistant", "content": response.content or ""}
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.name, "arguments": tc.arguments},
                }
                for tc in response.tool_calls
            ]
            messages.append(assistant_msg)

            # Execute each tool call
            for tc in response.tool_calls:
                result = await self._execute_tool(tc)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

        # Max iterations reached
        logger.warning(f"Max iterations ({self.max_iterations}) reached")
        await self._send_response(
            msg,
            "I've been working on this for a while. Here's what I found so far."
        )

    async def _execute_tool(self, tc: ToolCallRequest) -> str:
        """Execute a tool call via MCP."""
        logger.debug(f"Executing tool: {tc.name}")
        try:
            result = await self.mcp.call_tool(tc.name, tc.arguments)
            return result
        except Exception as e:
            error_msg = f"Tool error: {e}"
            logger.error(error_msg)
            return error_msg

    async def _send_response(self, msg: InboundMessage, content: str) -> None:
        """Send a response back to the channel."""
        response = OutboundMessage(
            channel=msg.channel,
            chat_id=msg.chat_id,
            content=content,
        )
        await self.bus.publish_outbound(response)
