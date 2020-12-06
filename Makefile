include ./Makefile.common

.PHONY: bucket

BUCKET_PREFIX ?= meta
STACK_NAME ?= docflow-api
REGION = us-east-1

bucketName := $(shell make -r -s -C ./infrastructure output)

OAS_URL = "s3://${bucketName}/${BUCKET_PREFIX}/swagger.yaml"

swagger.yaml:
	@${MAKE} -i -s -C ./infrastructure build
	@aws s3 cp swagger.yaml ${OAS_URL}

build:
	@sam build --use-container

deploy: swagger.yaml
	@aws s3 cp swagger.yaml ${OAS_URL}
	@sam deploy \
		--stack-name $(STACK_NAME) \
		--region $(REGION) \
		--s3-bucket $(bucketName) \
		--s3-prefix $(BUCKET_PREFIX) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM

clean:
	@aws s3 rm s3://${bucketName}/${BUCKET_PREFIX} --recursive
	@aws cloudformation delete-stack --stack-name $(STACK_NAME) --region $(REGION)

local:
	@sam local start-api

