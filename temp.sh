aws cloudformation deploy \
  --template-file dynamodb-cf.yaml \
  --stack-name marian-dynamodb \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation deploy \
  --template-file lambda-role-cf.yaml \
  --stack-name marian-lambda-role \
  --capabilities CAPABILITY_NAMED_IAM

aws cloudformation deploy \
  --template-file lambda-config-cf.yaml \
  --stack-name marian-lambda-config \
  --parameter-overrides LambdaLayerArn=YOUR_LAYER_ARN \
  --capabilities CAPABILITY_NAMED_IAM
