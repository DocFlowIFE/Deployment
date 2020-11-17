# Docflow


You have to have access key id and secret access key available either in ~/.aws/credentials or as environment variables.
To deploy the application use: 
```
make build deploy
```
For Lambda development use:
```
make build local
```

Remember to delete all resources from the AWS console not to waste money, it is limited!

# Requirements
* aws-sam-cli https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
* aws-cli https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html