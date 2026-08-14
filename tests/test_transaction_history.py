```python
import pytest
import requests

@pytest.mark.usefixtures("base_url", "auth_headers")
class TestUserAuthentication:
    def test_valid_credentials(self, base_url, auth_headers):
        login_url = f"{base_url}/login"
        credentials = {"username": "testuser", "password": "testpassword"}
        response = requests.post(login_url, json=credentials)
        assert response.status_code == 200
        assert "dashboard" in response.json()["redirect_url"]

    def test_invalid_credentials(self, base_url):
        login_url = f"{base_url}/login"
        credentials = {"username": "invaliduser", "password": "invalidpassword"}
        response = requests.post(login_url, json=credentials)
        assert response.status_code == 401
        assert "invalid credentials" in response.json()["error_message"]

    def test_empty_credentials(self, base_url):
        login_url = f"{base_url}/login"
        credentials = {"username": "", "password": ""}
        response = requests.post(login_url, json=credentials)
        assert response.status_code == 400
        assert "username and password are required" in response.json()["error_message"]

    def test_authenticated_user(self, base_url, auth_headers):
        dashboard_url = f"{base_url}/dashboard"
        response = requests.get(dashboard_url, headers=auth_headers)
        assert response.status_code == 200
        assert "dashboard" in response.json()["page_title"]
```