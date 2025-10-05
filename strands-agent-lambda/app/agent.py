"""Wrapper around the Strands agent SDK."""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping

from .config import Settings, configure_logging, get_settings
from .tools import load_tools, validate_tools

logger = logging.getLogger(__name__)


@dataclass
class AgentInvocation:
    """Normalized payload for interacting with a Strands agent."""

    messages: List[Mapping[str, Any]]
    metadata: Dict[str, Any]


class StrandsAgentRunner:
    """Encapsulates configuration and invocation logic for the Strands agent."""

    def __init__(
        self,
        settings: Settings | None = None,
        tools: Iterable[Any] | None = None,
    ) -> None:
        configure_logging((settings or get_settings()).log_level)
        self.settings = settings or get_settings()
        self._agent = self._create_agent(tools)

    def _create_agent(self, tools: Iterable[Any] | None = None) -> Any:
        try:
            module = importlib.import_module("strands_agents")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "The 'strands-agents' package is required to run this project."
            ) from exc

        agent_cls = getattr(module, "Agent", None)
        if agent_cls is None:
            raise RuntimeError("strands_agents.Agent class not found; check the SDK version")

        init_kwargs: MutableMapping[str, Any] = {
            "agent_id": self.settings.strands_agent_id,
            "api_key": self.settings.strands_api_key,
            "request_timeout": self.settings.request_timeout,
        }
        if self.settings.strands_api_base_url:
            init_kwargs["base_url"] = self.settings.strands_api_base_url

        loaded_tools = validate_tools(tools if tools is not None else load_tools(self.settings.enable_tools))
        if loaded_tools:
            init_kwargs["tools"] = loaded_tools

        logger.debug("Initializing Strands agent with kwargs: %s", {k: v for k, v in init_kwargs.items() if k != "api_key"})
        return agent_cls(**init_kwargs)

    def _build_payload(self, event: Mapping[str, Any]) -> AgentInvocation:
        if not isinstance(event, Mapping):
            raise ValueError("Event must be a mapping type")

        metadata: Dict[str, Any] = {}
        metadata.update(self.settings.default_metadata)
        event_metadata = event.get("metadata")
        if isinstance(event_metadata, Mapping):
            metadata.update(event_metadata)

        if "conversation_id" in event and "conversation_id" not in metadata:
            metadata["conversation_id"] = event["conversation_id"]

        messages = event.get("messages")
        if isinstance(messages, list) and all(isinstance(item, Mapping) for item in messages):
            normalized_messages = [dict(message) for message in messages]
        else:
            user_input = event.get("input")
            if isinstance(user_input, str) and user_input.strip():
                normalized_messages = [{"role": "user", "content": user_input.strip()}]
            else:
                raise ValueError("Event must contain 'messages' or a non-empty 'input'.")

        return AgentInvocation(messages=normalized_messages, metadata=metadata)

    def run(self, event: Mapping[str, Any]) -> Any:
        payload = self._build_payload(event)
        logger.info("Invoking Strands agent with %d message(s)", len(payload.messages))
        response = self._agent.invoke(messages=payload.messages, metadata=payload.metadata)
        logger.debug("Strands agent responded with: %s", response)
        return response
