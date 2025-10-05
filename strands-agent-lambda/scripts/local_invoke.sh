#!/usr/bin/env bash
set -euo pipefail

: "${IMAGE_NAME:=strands-agent-lambda:local}"
: "${EVENT_FILE:=event.sample.json}"

if [[ ! -f "${EVENT_FILE}" ]]; then
  echo "Event file '${EVENT_FILE}' not found" >&2
  exit 1
fi

docker build -t "${IMAGE_NAME}" -f Dockerfile .

CONTAINER_ID=$(docker run -d --rm -p 9000:8080 \
  -e STRANDS_AGENT_ID \
  -e STRANDS_API_KEY \
  -e STRANDS_API_BASE_URL \
  -e LOG_LEVEL \
  -e REQUEST_TIMEOUT \
  -e ENABLE_TOOLS \
  -e DEFAULT_METADATA \
  "${IMAGE_NAME}")

cleanup() {
  docker logs "${CONTAINER_ID}" --tail 20 || true
  docker stop "${CONTAINER_ID}" >/dev/null
}

trap cleanup EXIT

sleep 2

if command -v jq >/dev/null 2>&1; then
  curl -s "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d "@${EVENT_FILE}" | jq '.'
else
  curl -s "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d "@${EVENT_FILE}"
fi
