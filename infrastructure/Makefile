include ../Makefile.common

BUCKET_PREFIX ?= meta
STACK_NAME ?= bucket-meta
REGION = us-east-1

build:
	@sam build --use-container

deploy:
	@sam deploy \
		--stack-name $(STACK_NAME) \
		--region $(REGION) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

bucketName:
	@aws cloudformation describe-stacks \
			--stack-name ${STACK_NAME} \
			--region ${REGION} \
			--output text \
			--query 'Stacks[].Outputs[].OutputValue'
