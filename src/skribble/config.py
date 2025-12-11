from __future__ import annotations

from dataclasses import dataclass

DEFAULT_API_BASE_URL = "https://api.skribble.com/v2"
DEFAULT_MANAGEMENT_BASE_URL = "https://api.skribble.com/management"
DEFAULT_API_BASE_EU_URL = "https://api.skribble.de/v2"
DEFAULT_MANAGEMENT_BASE_EU_URL = "https://api.skribble.de/management"
# From Skribble auth docs: access token ~20 minutes lifetime
DEFAULT_ACCESS_TOKEN_TTL_SECONDS = 20 * 60


@dataclass
class SkribbleConfig:
    """
    Configuration for SkribbleClient behavior.
    """

    api_base_url: str = DEFAULT_API_BASE_URL
    management_base_url: str = DEFAULT_MANAGEMENT_BASE_URL
    timeout: int = 30
    verify_ssl: bool = True
    user_agent: str = "skribble-sdk/0.1.4"
    access_token_ttl_seconds: int = DEFAULT_ACCESS_TOKEN_TTL_SECONDS
    redis_key_prefix: str = "skribble"

@dataclass
class SkribbleEUConfig(SkribbleConfig):
    """
    Configuration for SkribbleClient behavior.
    """

    api_base_url: str = DEFAULT_API_BASE_EU_URL
    management_base_url: str = DEFAULT_MANAGEMENT_BASE_EU_URL
