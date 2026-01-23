"""Client factory for NocoDB CLI."""

from typing import Optional

from nocodb import APIToken, JWTAuthToken
from nocodb.infra.requests_client import NocoDBRequestsClient

from .config import Config


def create_client(config: Config) -> NocoDBRequestsClient:
    """Create a NocoDB client from configuration.

    Args:
        config: CLI configuration object

    Returns:
        Configured NocoDBRequestsClient instance

    Raises:
        ValueError: If configuration is missing required fields
    """
    missing = config.get_missing_fields()
    if missing:
        raise ValueError(
            f"Missing required configuration: {', '.join(missing)}. "
            "Set via --url/--token flags, NOCODB_URL/NOCODB_TOKEN env vars, "
            "or ~/.nocodbrc config file."
        )

    token = config.token
    if token.startswith("eyJ"):
        auth = JWTAuthToken(token)
    else:
        auth = APIToken(token)

    return NocoDBRequestsClient(auth, config.url)


def get_base_id(config: Config, base_id: Optional[str] = None) -> str:
    """Get base ID from argument or config.

    Args:
        config: CLI configuration
        base_id: Explicit base ID (takes priority)

    Returns:
        Base ID string

    Raises:
        ValueError: If no base ID available
    """
    result = base_id or config.base_id
    if not result:
        raise ValueError(
            "Base ID is required. Specify with -b/--base-id flag, "
            "NOCODB_BASE_ID env var, or base_id in config file."
        )
    return result
