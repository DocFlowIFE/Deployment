import json
import logging
import os

import boto3

logger = logging.getLogger(__name__)

ADMIN_POOL_ID = os.environ['ADMIN_POOL_ID']

def handler(event, context):
    client = boto3.client('cognito-idp')

    response = client.list_users(UserPoolId=ADMIN_POOL_ID)
    print(response)
    return {
        "statusCode": 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*'
        },
        "body": json.dumps([user['Username'] for user in response['Users']]),
    }
