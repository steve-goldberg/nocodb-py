"""Configuration for nocobot - NocoDB Telegram Agent."""

from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Nocobot configuration loaded from environment variables."""

    # Telegram
    telegram_token: str
    telegram_allow_from: list[str] = []

    # OpenRouter LLM
    openrouter_api_key: str
    openrouter_model: str = "anthropic/claude-sonnet-4"

    # NocoDB MCP Server
    nocodb_mcp_url: str = "http://ncdbmcp.lab/mcp"

    model_config = {
        "env_prefix": "",
        "env_file": ".env",
        "extra": "ignore",
    }


def load_config() -> Config:
    """Load configuration from environment."""
    return Config()
