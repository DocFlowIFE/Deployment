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

user_api_url = pytest.fixture(
    _output_value('PublicAPIEndpoint'),
    scope='session',
)

admin_pool_id = pytest.fixture(
    _output_value('AdminPoolId'),
    scope='session',
)

admin_client_id = pytest.fixture(
    _output_value('AdminClientId'),
    scope='session',
)

admin_api_url = pytest.fixture(
    _output_value(
        'AdminAPIEndpoint'
    ),
    scope='session',
)

@pytest.fixture(scope='session')
def faker_locale():
    return 'en-US'

@pytest.fixture(scope='session')
def user_token(cognito_idp_client, user_pool_id, user_client_id):
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
    return auth_resp['AuthenticationResult']['IdToken']

@pytest.fixture(scope='session')
def user_session(user_token):
    session = requests.Session()
    session.headers.update({
        'Authorization': user_token,
    })
    yield session

@pytest.fixture(scope='session')
def username():
    fake = faker.Faker()
    return fake.email()

@pytest.fixture(scope='session')
def admin_token(cognito_idp_client, admin_pool_id, admin_client_id, username):
    fake = faker.Faker()
    password = fake.password(24)
    new_password = fake.password(24)

    user = cognito_idp_client.admin_create_user(
        UserPoolId=admin_pool_id,
        Username=username,
        TemporaryPassword=password,
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

    auth_resp = cognito_idp_client.initiate_auth(
        ClientId=admin_client_id,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': password
        },
    )

    cognito_idp_client.admin_respond_to_auth_challenge(
        UserPoolId=admin_pool_id,
        ClientId=admin_client_id,
        ChallengeName='NEW_PASSWORD_REQUIRED',
        ChallengeResponses={
            "USERNAME": username,
            "NEW_PASSWORD": new_password,
        },
        Session=auth_resp['Session'],
    )

    auth_resp = cognito_idp_client.initiate_auth(
        ClientId=admin_client_id,
        AuthFlow='USER_PASSWORD_AUTH',
        AuthParameters={
            'USERNAME': username,
            'PASSWORD': new_password
        },
    )
    print(auth_resp['AuthenticationResult']['IdToken'])
    return auth_resp['AuthenticationResult']['IdToken']

@pytest.fixture(scope='session')
def admin_session(admin_token):
    session = requests.Session()
    session.headers.update({
        'Authorization': admin_token,
    })
    yield session
