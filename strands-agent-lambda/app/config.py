"""Configuration management for the Strands Agent Lambda."""

from __future__ import annotations

import logging
from functools import lru_cache
import json
from typing import Any, Dict

from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    strands_agent_id: str = Field(..., env="STRANDS_AGENT_ID", description="Unique identifier of the Strands agent to invoke.")
    strands_api_key: str = Field(..., env="STRANDS_API_KEY", description="API key used to authenticate with Strands services.")
    strands_api_base_url: str | None = Field(
        default=None,
        env="STRANDS_API_BASE_URL",
        description="Optional override for the Strands API base URL.",
    )
    log_level: str = Field("INFO", env="LOG_LEVEL", description="Application log level.")
    request_timeout: int = Field(30, env="REQUEST_TIMEOUT", description="Timeout in seconds for outbound requests.")
    enable_tools: bool = Field(True, env="ENABLE_TOOLS", description="Whether to load default Strands tools.")
    default_metadata: Dict[str, str] = Field(
        default_factory=dict,
        env="DEFAULT_METADATA",
        description="JSON-encoded dictionary merged into every invocation's metadata.",
    )

    @validator("default_metadata", pre=True)
    def _parse_default_metadata(cls, value: Any) -> Dict[str, str]:  # type: ignore[override]
        if isinstance(value, dict):
            return value
        if isinstance(value, str) and value:
            try:
                parsed = json.loads(value)
                if isinstance(parsed, dict):
                    return {str(k): str(v) for k, v in parsed.items()}
            except json.JSONDecodeError as exc:  # pragma: no cover - defensive logging path
                logging.getLogger(__name__).warning("Failed to parse DEFAULT_METADATA: %s", exc)
        return {}

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        arbitrary_types_allowed = True


@lru_cache(maxsize=1)
def get_settings(**overrides: Any) -> Settings:
    """Return cached application settings.

    Parameters
    ----------
    overrides:
        Optional keyword arguments used to override environment-derived values.
    """

    if overrides:
        logging.getLogger(__name__).debug("Overriding settings with %s", overrides)
    return Settings(**overrides)


def configure_logging(level: str | None = None) -> None:
    """Configure root logging for the Lambda runtime."""

    logging.basicConfig(level=getattr(logging, (level or "INFO").upper(), logging.INFO))
