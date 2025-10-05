"""AWS Lambda handler for invoking a Strands agent."""

from __future__ import annotations

import json
import logging
from typing import Any, Mapping, MutableMapping

from .agent import StrandsAgentRunner
from .config import get_settings

logger = logging.getLogger(__name__)


def _serialize_response(response: Any) -> str:
    if isinstance(response, str):
        return response
    return json.dumps(response, default=str)


def handler(event: Mapping[str, Any] | None, context: Any | None) -> MutableMapping[str, Any]:
    """Entrypoint for AWS Lambda."""

    settings = get_settings()
    runner = StrandsAgentRunner(settings=settings)

    try:
        result = runner.run(event or {})
        body = _serialize_response(result)
        return {"statusCode": 200, "body": body}
    except ValueError as exc:
        logger.exception("Invalid invocation payload")
        return {"statusCode": 400, "body": json.dumps({"error": str(exc)})}
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.exception("Unhandled error from Strands agent invocation")
        return {"statusCode": 500, "body": json.dumps({"error": str(exc)})}
