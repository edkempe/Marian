# File: deploy-test.sh
# Project: MARIAN (Project HAL)
# Purpose: Create and upload Lambda deployment package with dependencies
# Author: Claude
# Date: December 15, 2024

#!/bin/bash
set -e

# Configuration
LAMBDA_FUNCTION_NAME="Marian"
LAYER_NAME="marian_dependencies"
REQUIREMENTS_FILE="requirements.txt"
LAMBDA_FILE="lambda_function.py"
AWS_REGION="us-east-1"

# Create clean directories
echo "Creating directories..."
rm -rf package layer
mkdir -p package layer/python

# Install dependencies for layer
echo "Installing dependencies..."
pip install --target ./layer/python -r $REQUIREMENTS_FILE

# Create layer ZIP file
echo "Creating layer ZIP..."
cd layer
zip -r9 ../marian_layer.zip .
cd ..

# Create function package
echo "Creating function package..."
cp $LAMBDA_FILE package/
cd package
zip -r9 ../marian_function.zip .
cd ..

# Upload layer to AWS
echo "Uploading layer to AWS..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "MARIAN dependencies" \
    --zip-file fileb://marian_layer.zip \
    --compatible-runtimes python3.9 \
    --region $AWS_REGION \
    --query 'Version' \
    --output text)

echo "Layer version created: $LAYER_VERSION"

# Update Lambda function
echo "Updating Lambda function..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://marian_function.zip \
    --region $AWS_REGION

# Update Lambda configuration to use new layer
LAYER_ARN="arn:aws:lambda:$AWS_REGION:$(aws sts get-caller-identity --query 'Account' --output text):layer:$LAYER_NAME:$LAYER_VERSION"
echo "Updating Lambda configuration with layer: $LAYER_ARN"

aws lambda update-function-configuration \
    --function-name $LAMBDA_FUNCTION_NAME \
    --layers $LAYER_ARN \
    --runtime python3.9 \
    --handler lambda_function.lambda_handler \
    --environment "Variables={DYNAMODB_TABLE=email_metadata,GMAIL_SECRET_ID=gmail/oauth/tokens,ANTHROPIC_SECRET_ID=AnthropicKey}"

# Clean up temp directories but keep zip files
echo "Cleaning up..."
rm -rf package layer

echo "Deployment complete!"
echo "Created and uploaded:"
echo "- marian_layer.zip (Lambda layer with dependencies)"
echo "- marian_function.zip (Lambda function code)"
