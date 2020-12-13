import pytest


def test_user(session, api_url):
    resp = session.get(f'{api_url}/documents/fe')
    
