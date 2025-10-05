# strands-agent-lambda

Production-ready template for running a [Strands](https://strands.ai) agent in an AWS Lambda function packaged as a container image.

## Features

- **Python 3.11** Lambda handler that proxies requests to a Strands Agent.
- **Containerized** using the official AWS Lambda Python base image.
- **Infrastructure automation** via reusable scripts and GitHub Actions (build, push to ECR, and update Lambda).
- **Configuration management** powered by environment variables and Pydantic validation.
- **Lightweight tests** to validate payload normalization and handler responses.

## Project layout

```
app/
  agent.py        # Wrapper for the Strands Agent SDK
  config.py       # Pydantic-based configuration helper
  handler.py      # AWS Lambda handler entrypoint
  tools.py        # Tool loading helper
scripts/
  build.sh        # Build and push image to ECR
  deploy.sh       # Update Lambda to latest image
  local_invoke.sh # Run the container locally and invoke via Lambda runtime API
```

Additional files include sample events, tests, CI workflow, and packaging metadata.

## Prerequisites

- Python 3.11+
- Docker
- AWS CLI v2 with credentials permitted to push to ECR and update Lambda
- An existing ECR repository and Lambda function configured for container images

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .[dev]
```

## Running tests

```bash
pytest
```

## Local invocation

Prepare environment variables (you can copy `.env.example` to `.env`):

```bash
export STRANDS_AGENT_ID=your-agent-id
export STRANDS_API_KEY=your-api-key
```

Invoke locally using Docker:

```bash
./scripts/local_invoke.sh
```

The script builds the container, runs it locally, then calls the Lambda runtime API with `event.sample.json`.

## Build and deploy

```bash
export AWS_ACCOUNT_ID=123456789012
export ECR_REPOSITORY=strands-agent-lambda
export LAMBDA_FUNCTION_NAME=strands-agent-lambda

./scripts/build.sh
./scripts/deploy.sh
```

`build.sh` logs into ECR, builds the container image, tags it with a timestamp, and pushes it to your repository. `deploy.sh` reuses the generated `image_uri.txt` (or accepts `IMAGE_URI`) and updates the specified Lambda function.

## Continuous delivery

The GitHub Actions workflow (`.github/workflows/ci.yml`) performs the following:

1. Installs dependencies and runs unit tests on every push and pull request.
2. On pushes to `main`, assumes the provided AWS role (`AWS_ROLE_ARN` secret), builds the container image, pushes it to the ECR repository defined by `ECR_REPOSITORY`, and updates the Lambda function indicated by `LAMBDA_FUNCTION_NAME`.

Required repository secrets:

- `AWS_ROLE_ARN`
- `AWS_REGION`
- `ECR_REPOSITORY`
- `LAMBDA_FUNCTION_NAME`

## Environment variables

| Variable | Required | Description |
| -------- | -------- | ----------- |
| `STRANDS_AGENT_ID` | ✅ | Identifier of the agent to invoke. |
| `STRANDS_API_KEY` | ✅ | API key for Strands. |
| `STRANDS_API_BASE_URL` | ❌ | Custom base URL for the Strands API. |
| `LOG_LEVEL` | ❌ | Logging level (default `INFO`). |
| `REQUEST_TIMEOUT` | ❌ | Request timeout in seconds (default `30`). |
| `ENABLE_TOOLS` | ❌ | Toggle loading of default Strands tools (default `true`). |
| `DEFAULT_METADATA` | ❌ | JSON metadata merged into every invocation. |

## Sample payload

```json
{
  "input": "Hello, can you summarize today's agenda?",
  "conversation_id": "demo-conversation",
  "metadata": {
    "source": "local-sample"
  }
}
```

## License

MIT
