```python
import pytest
import requests

@pytest.mark.usefixtures("base_url", "auth_headers")
class TestUserAuthentication:
    def test_valid_login(self, base_url, auth_headers):
        login_url = f"{base_url}/login"
        valid_credentials = {"username": "test_user", "password": "test_password"}
        response = requests.post(login_url, json=valid_credentials)
        assert response.status_code == 200
        assert "dashboard" in response.json()["redirect_url"]

    def test_invalid_login(self, base_url):
        login_url = f"{base_url}/login"
        invalid_credentials = {"username": "invalid_user", "password": "invalid_password"}
        response = requests.post(login_url, json=invalid_credentials)
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["error_message"]

    def test_empty_credentials(self, base_url):
        login_url = f"{base_url}/login"
        empty_credentials = {"username": "", "password": ""}
        response = requests.post(login_url, json=empty_credentials)
        assert response.status_code == 400
        assert "username and password are required" in response.json()["error_message"]

    def test_missing_credentials(self, base_url):
        login_url = f"{base_url}/login"
        missing_credentials = {"username": "test_user"}
        response = requests.post(login_url, json=missing_credentials)
        assert response.status_code == 400
        assert "password is required" in response.json()["error_message"]
```