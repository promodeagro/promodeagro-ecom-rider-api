import requests

BASE_URL = "http://localhost:3000"

def test_signin():
    response = requests.post(f"{BASE_URL}/signin", json={"phone": "1234567890"})
    assert response.status_code == 200
    assert "otp" in response.json() or "message" in response.json()

def test_validate_otp():
    # Replace '123456' with a valid OTP for real testing
    response = requests.post(f"{BASE_URL}/validate-otp", json={"phone": "1234567890", "otp": "123456"})
    assert response.status_code in [200, 400, 401]

def test_refresh_token():
    # Replace 'dummy_token' with a valid refresh token for real testing
    response = requests.post(f"{BASE_URL}/refresh-token", json={"refresh_token": "dummy_token"})
    assert response.status_code in [200, 400, 401] 