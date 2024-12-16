# File: deploy-test.sh
# Project: MARIAN (Project HAL)
# Purpose: Test script for chunked deployment of Lambda layers
# Author: Claude
# Date: December 15, 2024

#!/bin/bash
set -e

# Configuration
LAMBDA_FUNCTION_NAME="Marian"
AWS_REGION="us-east-1"
LAYER_NAME="marian_dependencies"

echo "Installing dependencies in chunks..."
mkdir -p layer/python

# Read requirements and install in smaller groups
while read -r requirement || [ -n "$requirement" ]; do
    if [[ ! -z "$requirement" && ! "$requirement" =~ ^# ]]; then
        echo "Installing: $requirement"
        pip install --target ./layer/python "$requirement"
    fi
done < requirements.txt

echo "Creating layer ZIP..."
cd layer
zip -r9 ../layer.zip .
cd ..

echo "Uploading layer..."
# Use AWS CLI with increased timeout
export AWS_CLIENT_TIMEOUT=300
aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.9 \
    --region $AWS_REGION

# Update Lambda function
echo "Updating Lambda function..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://function.zip \
    --region $AWS_REGION

# Clean up
rm -rf layer layer.zip