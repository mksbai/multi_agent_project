"""Helpers for loading Strands agent tools."""

from __future__ import annotations

import importlib
import logging
from typing import Any, Iterable, List

logger = logging.getLogger(__name__)


def load_tools(enable: bool = True, **kwargs: Any) -> List[Any]:
    """Load default tools from ``strands_agents_tools`` when available."""

    if not enable:
        logger.debug("Tool loading disabled via configuration.")
        return []

    try:
        module = importlib.import_module("strands_agents_tools")
    except ModuleNotFoundError:  # pragma: no cover - executed only when dependency missing
        logger.info("strands_agents_tools package not installed; continuing without tools")
        return []

    loader = getattr(module, "load_default_tools", None)
    if callable(loader):
        tools = list(loader(**kwargs))
        logger.debug("Loaded %d tool(s) from strands_agents_tools", len(tools))
        return tools

    logger.info("strands_agents_tools.load_default_tools() not found; no tools loaded")
    return []


def validate_tools(tools: Iterable[Any]) -> List[Any]:
    """Ensure the provided tools are in a list for downstream consumption."""

    return [tool for tool in tools]
