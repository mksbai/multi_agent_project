#!/usr/bin/env bash
set -euo pipefail

: "${AWS_REGION:=us-east-1}"
: "${LAMBDA_FUNCTION_NAME?Set LAMBDA_FUNCTION_NAME to the target Lambda function}" 

if [[ -f image_uri.txt ]];
then
  IMAGE_URI="$(cat image_uri.txt)"
else
  : "${IMAGE_URI?Set IMAGE_URI to the pushed container image URI or run scripts/build.sh first}"
fi

aws lambda update-function-code \
  --region "${AWS_REGION}" \
  --function-name "${LAMBDA_FUNCTION_NAME}" \
  --image-uri "${IMAGE_URI}"

echo "Lambda function ${LAMBDA_FUNCTION_NAME} updated with image ${IMAGE_URI}" >&2
