```python
import pytest
import requests
from conftest import base_url, auth_headers

def test_user_login(base_url, auth_headers):
    login_url = f"{base_url}/login"
    valid_credentials = {"username": "test_user", "password": "test_password"}
    response = requests.post(login_url, json=valid_credentials, headers=auth_headers)
    assert response.status_code == 200
    assert "dashboard" in response.json()["redirect_url"]

def test_user_login_invalid_credentials(base_url, auth_headers):
    login_url = f"{base_url}/login"
    invalid_credentials = {"username": "invalid_user", "password": "invalid_password"}
    response = requests.post(login_url, json=invalid_credentials, headers=auth_headers)
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["error_message"]

def test_user_login_missing_credentials(base_url, auth_headers):
    login_url = f"{base_url}/login"
    missing_credentials = {"username": "test_user"}
    response = requests.post(login_url, json=missing_credentials, headers=auth_headers)
    assert response.status_code == 400
    assert "missing credentials" in response.json()["error_message"]

def test_user_login_empty_credentials(base_url, auth_headers):
    login_url = f"{base_url}/login"
    empty_credentials = {}
    response = requests.post(login_url, json=empty_credentials, headers=auth_headers)
    assert response.status_code == 400
    assert "empty credentials" in response.json()["error_message"]
```