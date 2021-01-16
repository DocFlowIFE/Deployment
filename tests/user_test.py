import pytest


def test_user(user_session, user_api_url):
    resp = user_session.get(f'{user_api_url}/tickets')
    assert resp.status_code == 200

@pytest.fixture(scope='session')
def ticket_template_id(admin_session, admin_api_url, user_api_url, username):
    resp = admin_session.post(f'{admin_api_url}/ticketTemplates', json={
        "users": [username],
        "description": "",
    })
    assert resp.status_code == 200
    return resp.json()['ticketTemplateId']


def test_create_ticket_template(admin_session, admin_api_url, username):
    resp = admin_session.post(f'{admin_api_url}/ticketTemplates', json={
        "users": [username],
        "description": "",
    })
    print(resp.json())
    assert resp.status_code == 200


def test_get_ticket_templates(admin_session, admin_api_url, username):
    resp = admin_session.get(f'{admin_api_url}/ticketTemplates')
    assert resp.status_code == 200

def test_create_ticket(user_session, user_api_url, ticket_template_id):
    resp = user_session.post(f'{user_api_url}/tickets', json={
        "ticketTemplateId": ticket_template_id,
        "comment": "",
    })
    assert resp.status_code == 200

def test_get_user_tickets(user_session, user_api_url):

    resp = user_session.get(f'{user_api_url}/tickets')
    assert resp.status_code == 200

def test_patch_ticket(user_session, user_api_url, admin_session, admin_api_url, ticket_template_id):
    resp = user_session.post(f'{user_api_url}/tickets', json={
        "ticketTemplateId": ticket_template_id,
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
