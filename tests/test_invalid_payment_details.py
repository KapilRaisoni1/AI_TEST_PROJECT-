```python
import pytest
import requests
from conftest import base_url, auth_headers

@pytest.mark.parametrize("username, password, expected_status_code", [
    ("valid_username", "valid_password", 200),
    ("invalid_username", "valid_password", 401),
    ("valid_username", "invalid_password", 401),
])
def test_user_authentication(base_url, auth_headers, username, password, expected_status_code):
    login_url = f"{base_url}/login"
    payload = {"username": username, "password": password}
    response = requests.post(login_url, headers=auth_headers, json=payload)
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        assert "dashboard" in response.json()["redirect_url"]

def test_dashboard_displayed_after_login(base_url, auth_headers):
    login_url = f"{base_url}/login"
    payload = {"username": "valid_username", "password": "valid_password"}
    response = requests.post(login_url, headers=auth_headers, json=payload)
    assert response.status_code == 200
    dashboard_url = response.json()["redirect_url"]
    response = requests.get(dashboard_url, headers=auth_headers)
    assert response.status_code == 200
    assert "dashboard" in response.text.lower()
```