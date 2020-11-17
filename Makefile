build:
	@sam build --use-container

deploy:
	@sam deploy --stack-name docflow-api --region us-east-1 --resolve-s3 --capabilities CAPABILITY_IAM

undeploy:
	@aws cloudformation delete-stack --stack-name docflow-api

local:
	@sam local start-api