.PHONY: install test docker-build docker-run deploy clean

install:
	pip install --upgrade pip
	pip install -e .[dev]

test:
	pytest --cov=app --cov-report=term-missing

docker-build:
	docker build -t strands-agent-lambda .

docker-run:
	docker run --rm -p 9000:8080 \
		-e STRANDS_AGENT_ID \
		-e STRANDS_API_KEY \
		strands-agent-lambda

deploy:
	AWS_ACCOUNT_ID=$${AWS_ACCOUNT_ID} ECR_REPOSITORY=$${ECR_REPOSITORY} ./scripts/build.sh
	LAMBDA_FUNCTION_NAME=$${LAMBDA_FUNCTION_NAME} ./scripts/deploy.sh

clean:
	rm -f image_uri.txt
	docker image rm strands-agent-lambda || true
