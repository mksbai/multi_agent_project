from __future__ import annotations

import json
import sys
import types

import pytest

from app.agent import StrandsAgentRunner
from app.config import Settings, get_settings


@pytest.fixture(autouse=True)
def stub_strands_sdks(monkeypatch: pytest.MonkeyPatch) -> None:
    agent_module = types.ModuleType("strands_agents")

    class DummyAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def invoke(self, **payload):
            return {"payload": payload, "kwargs": self.kwargs}

    agent_module.Agent = DummyAgent
    monkeypatch.setitem(sys.modules, "strands_agents", agent_module)

    tools_module = types.ModuleType("strands_agents_tools")

    def load_default_tools(**kwargs):
        return ["demo-tool"]

    tools_module.load_default_tools = load_default_tools
    monkeypatch.setitem(sys.modules, "strands_agents_tools", tools_module)

    yield

    monkeypatch.delitem(sys.modules, "strands_agents", raising=False)
    monkeypatch.delitem(sys.modules, "strands_agents_tools", raising=False)


@pytest.fixture(autouse=True)
def configure_env(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("STRANDS_AGENT_ID", "agent-123")
    monkeypatch.setenv("STRANDS_API_KEY", "api-key")
    yield
    get_settings.cache_clear()


def test_runner_builds_payload_from_input() -> None:
    settings = Settings(strands_agent_id="agent-123", strands_api_key="api-key")
    runner = StrandsAgentRunner(settings=settings)
    response = runner.run({"input": "Hello"})

    assert response["payload"]["messages"][0]["content"] == "Hello"
    assert response["payload"]["metadata"] == {}


def test_runner_builds_payload_from_messages() -> None:
    settings = Settings(strands_agent_id="agent-123", strands_api_key="api-key")
    runner = StrandsAgentRunner(settings=settings)

    response = runner.run(
        {
            "messages": [
                {"role": "user", "content": "Ping"},
                {"role": "assistant", "content": "Pong"},
            ],
            "metadata": {"foo": "bar"},
        }
    )

    assert len(response["payload"]["messages"]) == 2
    assert response["payload"]["metadata"]["foo"] == "bar"


def test_runner_validates_event() -> None:
    settings = Settings(strands_agent_id="agent-123", strands_api_key="api-key")
    runner = StrandsAgentRunner(settings=settings)

    with pytest.raises(ValueError):
        runner.run({})


def test_default_metadata_is_merged(monkeypatch: pytest.MonkeyPatch) -> None:
    metadata = {"team": "ml"}
    monkeypatch.setenv("DEFAULT_METADATA", json.dumps(metadata))
    get_settings.cache_clear()
    settings = get_settings()

    runner = StrandsAgentRunner(settings=settings)
    result = runner.run({"input": "hi", "metadata": {"request": "123"}})

    assert result["payload"]["metadata"]["team"] == "ml"
    assert result["payload"]["metadata"]["request"] == "123"
