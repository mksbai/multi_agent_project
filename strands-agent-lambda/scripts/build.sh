#!/usr/bin/env bash
set -euo pipefail

: "${AWS_REGION:=us-east-1}"
: "${IMAGE_TAG:=$(date +%Y%m%d%H%M%S)}"
: "${IMAGE_NAME:=strands-agent-lambda}"
: "${AWS_ACCOUNT_ID?Set AWS_ACCOUNT_ID to your AWS account ID}"
: "${ECR_REPOSITORY?Set ECR_REPOSITORY to the target ECR repository name}"

ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_URI="${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" -f Dockerfile .
docker tag "${IMAGE_NAME}:${IMAGE_TAG}" "${IMAGE_URI}"
docker push "${IMAGE_URI}"

echo "${IMAGE_URI}" | tee image_uri.txt
