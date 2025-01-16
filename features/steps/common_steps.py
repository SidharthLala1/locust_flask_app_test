import requests

BASE_URL = "http://127.0.0.1:5000"  # Update with actual server URL

def register_user(payload):
    """Registers a user and returns the response."""
    return requests.post(f"{BASE_URL}/client_registeration", json=payload)

def login_user(credentials):
    """Logs in a user and returns the response."""
    return requests.post(f"{BASE_URL}/client_login", json=credentials)
