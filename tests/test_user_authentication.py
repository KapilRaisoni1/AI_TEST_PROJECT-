```python
import pytest
import requests
from conftest import base_url, auth_headers

def test_user_authentication(base_url, auth_headers):
    # Given user is on login page
    login_url = f"{base_url}/login"
    response = requests.get(login_url)
    assert response.status_code == 200

    # When user enters valid credentials
    valid_credentials = {"username": "test_user", "password": "test_password"}
    response = requests.post(login_url, json=valid_credentials, headers=auth_headers)
    assert response.status_code == 200

    # Then dashboard should be displayed
    dashboard_url = f"{base_url}/dashboard"
    response = requests.get(dashboard_url, headers=auth_headers)
    assert response.status_code == 200
    assert "Dashboard" in response.text

def test_invalid_credentials(base_url, auth_headers):
    # Given user is on login page
    login_url = f"{base_url}/login"
    response = requests.get(login_url)
    assert response.status_code == 200

    # When user enters invalid credentials
    invalid_credentials = {"username": "invalid_user", "password": "invalid_password"}
    response = requests.post(login_url, json=invalid_credentials, headers=auth_headers)
    assert response.status_code == 401

def test_missing_credentials(base_url, auth_headers):
    # Given user is on login page
    login_url = f"{base_url}/login"
    response = requests.get(login_url)
    assert response.status_code == 200

    # When user enters missing credentials
    missing_credentials = {"username": "test_user"}
    response = requests.post(login_url, json=missing_credentials, headers=auth_headers)
    assert response.status_code == 400

def test_empty_credentials(base_url, auth_headers):
    # Given user is on login page
    login_url = f"{base_url}/login"
    response = requests.get(login_url)
    assert response.status_code == 200

    # When user enters empty credentials
    empty_credentials = {}
    response = requests.post(login_url, json=empty_credentials, headers=auth_headers)
    assert response.status_code == 400
```