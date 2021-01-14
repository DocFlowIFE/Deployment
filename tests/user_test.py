import pytest


def test_user(session, api_url):
    resp = session.get(f'{api_url}/tickets')
    assert resp.status_code == 200


def test_create_ticket(session, api_url):
    resp = session.post(f'{api_url}/ticketTamplates', json={})
    assert resp.status_code == 200