#!/bin/bash

# Test AWS connectivity
echo "Testing AWS STS..."
aws sts get-caller-identity

# List existing layers
echo "Listing existing layers..."
aws lambda list-layers

# Try uploading a minimal test layer
echo "Creating test layer..."
mkdir -p test_layer/python
echo "print('test')" > test_layer/python/test.py
cd test_layer
zip -r ../test_layer.zip .
cd ..

echo "Uploading test layer..."
aws lambda publish-layer-version \
    --layer-name "test_layer" \
    --zip-file fileb://test_layer.zip \
    --compatible-runtimes python3.9

# Cleanup
rm -rf test_layer test_layer.zip