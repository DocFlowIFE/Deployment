include ./Makefile.common

.PHONY: bucket

BUCKET_PREFIX ?= meta
STACK_NAME ?= docflow-api
REGION = us-east-1

BUCKET_NAME := $(shell make -r -s -C ./infrastructure output)

OAS_URL = "s3://${BUCKET_NAME}/${BUCKET_PREFIX}/swagger.yaml"

PARAMETER_OVERRIDES = --parameter-overrides \
    TemplateBucket=$(BUCKET_NAME) \
    TemplateBucketPrefix=$(BUCKET_PREFIX)

swagger.yaml:
	@${MAKE} -i -s -C ./infrastructure build
	@aws s3 cp swagger.yaml ${OAS_URL}

build:
	@rm -rf .aws-sam
	@sam build --use-container

deploy: swagger.yaml
	@aws s3 cp swagger.yaml ${OAS_URL}
	@sam deploy \
		--stack-name $(STACK_NAME) \
		--region $(REGION) \
		--s3-bucket $(BUCKET_NAME) \
		--s3-prefix $(BUCKET_PREFIX) \
		--capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
		$(PARAMETER_OVERRIDES)

clean:
	@aws s3 rm s3://${BUCKET_NAME}/${BUCKET_PREFIX} --recursive
	@aws cloudformation delete-stack --stack-name $(STACK_NAME) --region $(REGION)

local:
	@sam local start-api

