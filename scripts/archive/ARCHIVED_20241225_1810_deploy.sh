#!/bin/bash
set -e

# Configuration
LAMBDA_FUNCTION_NAME="Marian"
AWS_REGION="us-east-1"
LAYER_NAME="marian_dependencies"

# Function to check and delete failed stack
cleanup_stack() {
    local stack_name=$1
    local stack_status=$(aws cloudformation describe-stacks --stack-name $stack_name --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "DOES_NOT_EXIST")
    
    if [ "$stack_status" = "ROLLBACK_COMPLETE" ]; then
        echo "Cleaning up failed stack: $stack_name"
        aws cloudformation delete-stack --stack-name $stack_name
        aws cloudformation wait stack-delete-complete --stack-name $stack_name
    fi
}

# Clean up any failed stacks
cleanup_stack "marian-lambda-role"
cleanup_stack "marian-lambda-config"

echo "Creating Lambda layer..."
# Create layer directory
rm -rf layer venv
mkdir -p layer/python

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install wheel
pip install --upgrade pip wheel

# Install dependencies into layer
pip install --platform manylinux2014_x86_64 \
    --implementation cp \
    --python-version 3.9 \
    --only-binary=:all: \
    -r requirements.txt \
    -t ./layer/python/

# Deactivate virtual environment
deactivate

# Create layer ZIP
cd layer
zip -r9 ../layer.zip .
cd ..

# Upload layer
echo "Uploading Lambda layer..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --description "MARIAN dependencies" \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.9 \
    --region $AWS_REGION \
    --query 'Version' \
    --output text)

LAYER_ARN="arn:aws:lambda:$AWS_REGION:$(aws sts get-caller-identity --query 'Account' --output text):layer:$LAYER_NAME:$LAYER_VERSION"
echo "Created layer: $LAYER_ARN"

# Deploy IAM policy
echo "Deploying IAM policy..."
aws cloudformation deploy \
    --template-file infrastructure/cloudformation/lambda-role.yaml \
    --stack-name marian-lambda-role \
    --capabilities CAPABILITY_NAMED_IAM \
    --no-fail-on-empty-changeset

# Package Lambda code
echo "Packaging Lambda function..."
rm -rf package
mkdir -p package
cp src/*.py package/
cd package
zip -r9 ../function.zip .
cd ..

# Update Lambda function code
echo "Updating Lambda function code..."
aws lambda update-function-code \
    --function-name $LAMBDA_FUNCTION_NAME \
    --zip-file fileb://function.zip \
    --region $AWS_REGION

# Update Lambda configuration
echo "Updating Lambda function configuration..."
aws lambda update-function-configuration \
    --function-name $L