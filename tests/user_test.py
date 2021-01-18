import pytest
import requests

@pytest.fixture(scope='session')
def ticket_template_id(admin_session, admin_api_url, user_api_url, username):
    resp = admin_session.post(f'{admin_api_url}/ticketTemplates', json={
        "users": [username],
        "description": "",
        "title": "Title of the template",
        "filename": "myfile",
    })
    assert resp.status_code == 200
    return resp.json()['ticketTemplateId']


def test_create_ticket_template(admin_session, admin_api_url, username):
    response = admin_session.post(f'{admin_api_url}/ticketTemplates', json={
        "users": [username],
        "description": "",
        "title": "Title of the template",
        "filename": "myfile",
    })
    assert response.status_code == 200
    response = response.json()['fileUploadLink']
    print(response)
    with open("myfile", 'rb') as f:
        files = {'file': (response['fields']['key'], f)}
        http_response = requests.post(response['url'], data=response['fields'], files=files)
    print(http_response)



def test_get_ticket_templates(user_session, user_api_url):
    resp = user_session.get(f'{user_api_url}/ticketTemplates')
    assert resp.status_code == 200
#
def test_create_ticket(user_session, user_api_url, ticket_template_id):
    resp = user_session.post(f'{user_api_url}/tickets', json={
        "ticketTemplateId": ticket_template_id,
        "comment": "",
        "filename": "myfile",
    })
    assert resp.status_code == 200
#
def test_get_user_tickets(user_session, user_api_url):

    resp = user_session.get(f'{user_api_url}/tickets')
    assert resp.status_code == 200

def test_patch_ticket(user_session, user_api_url, admin_session, admin_api_url, ticket_template_id):
    resp = user_session.post(f'{user_api_url}/tickets', json={
        "ticketTemplateId": ticket_template_id,
        "filename": "myfile",
        "comment": "",
    })
    assert resp.status_code == 200
    print(resp, resp.json())
    ticket_id = resp.json()['ticketId']

    resp = admin_session.patch(f'{admin_api_url}/tickets/{ticket_id}', json={
        "status": "accepted",
        "comment": "New comment",
    })
    assert resp.status_code == 200
    print(resp, resp.json())

    resp = user_session.get(f'{user_api_url}/tickets')
    assert resp.status_code == 200

def test_get_users(admin_session, admin_api_url):

    resp = admin_session.get(f'{admin_api_url}/users')
    assert resp.status_code == 200
