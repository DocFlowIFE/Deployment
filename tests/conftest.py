import operator

import boto3
import faker
import pytest
import requests

def _stack_outputs(cfn_client):
    return cfn_client.describe_stacks(StackName='docflow-api')['Stacks'][0]['Outputs']

def _output_value(output_key):
    def wrap(cfn_client):
        stack_outputs = getattr(_output_value, 'cache', [])
        if not stack_outputs:
            stack_outputs = _stack_outputs(cfn_client)
            setattr(_output_value, 'cache', stack_outputs)
        return str(
            next(
                map(
                    operator.itemgetter('OutputValue'),
                    filter(
                        lambda k: k['OutputKey'] == output_key,
                        stack_outputs
                    )
                )
            )
        )
    return wrap

def _aws_client(client_id):
    return lambda: boto3.client(client_id)

cfn_client = pytest.fixture(
    _aws_client('cloudformation'),
    scope='session',
)

cognito_idp_client = pytest.fixture(
    _aws_client('cognito-idp'),
    scope='session',
)

user_pool_id = pytest.fixture(
    _output_value('UserPoolId'),
    scope='session',
)

user_client_id = pytest.fixture(
    _output_value('UserClientId'),
    scope='session',
)

api_url = pytest.fixture(
    _output_value(
        'PublicAPIEndpoint'
    )
)

@pytest.fixture(scope='session')
def faker_locale():
    return 'en-US'

@pytest.fixture(scope='session')
def token(cognito_idp_client, user_pool_id, user_client_id):
    fake = faker.Faker()
    username = fake.email()
    password = fake.password(24)

    user = cognito_idp_client.sign_up(
        ClientId = user_client_id,
        Username = username,
        Password = password,
        UserAttributes=[
            {
                'Name': 'name',
                'Value': fake.name(),
            },
            {
                'Name': 'email',
                'Value': username,
            }
        ]
        )
    cognito_idp_client.admin_confirm_sign_up(
        UserPoolId=user_pool_id,
        Username=username,
    )

    auth_resp = cognito_idp_client.initiate_auth(
        ClientId = user_client_id,
        AuthFlow = 'USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        },
    )
    print(auth_resp)
    return auth_resp['AuthenticationResult']['IdToken']

@pytest.fixture(scope='session')
def session(token):
    session = requests.Session()
    session.headers.update({
        'Authorization': token,
    })
    yield session