from __future__ import annotations

import json
import sys
import types

import pytest

from app.config import get_settings


@pytest.fixture(autouse=True)
def stub_sdks(monkeypatch: pytest.MonkeyPatch) -> None:
    agent_module = types.ModuleType("strands_agents")

    class DummyAgent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def invoke(self, **payload):
            return {"payload": payload}

    agent_module.Agent = DummyAgent
    monkeypatch.setitem(sys.modules, "strands_agents", agent_module)

    tools_module = types.ModuleType("strands_agents_tools")

    def load_default_tools(**kwargs):
        return []

    tools_module.load_default_tools = load_default_tools
    monkeypatch.setitem(sys.modules, "strands_agents_tools", tools_module)
    yield
    monkeypatch.delitem(sys.modules, "strands_agents", raising=False)
    monkeypatch.delitem(sys.modules, "strands_agents_tools", raising=False)


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("STRANDS_AGENT_ID", "agent-123")
    monkeypatch.setenv("STRANDS_API_KEY", "api-key")
    yield
    get_settings.cache_clear()


def test_handler_returns_success(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.handler import handler

    response = handler({"input": "Hello"}, None)
    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["payload"]["messages"][0]["content"] == "Hello"


def test_handler_returns_bad_request(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.handler import handler

    response = handler({}, None)
    assert response["statusCode"] == 400
