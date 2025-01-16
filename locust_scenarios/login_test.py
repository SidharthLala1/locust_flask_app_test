from locust import HttpUser, task, between, events
import json
import random
import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.test_config import TestConfig


class LoginTestUser(HttpUser):
    wait_time = between(TestConfig.MIN_WAIT_TIME // 1000, TestConfig.MAX_WAIT_TIME // 1000)

    def on_start(self):
        """Initialize test data"""
        # Valid users for testing
        self.valid_users = [
            {"email": f"user{i}@example.com", "password": "password123"}
            for i in range(100)
        ]

        # Invalid users for negative testing
        self.invalid_users = [
            {"email": "nonexistent@example.com", "password": "wrongpass"},
            {"email": "invalid.email", "password": "password123"},
            {"email": "", "password": "password123"},
            {"email": "user@example.com", "password": ""},
            {"email": "user@example.com", "password": "short"},
        ]

        # Users with special characters
        self.special_users = [
            {"email": "user+test@example.com", "password": "pass'word123"},
            {"email": "user@sub.example.com", "password": "pass\"word123"},
            {"email": "user.name@example.com", "password": "pass@word123"}
        ]

        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    def log_response(self, response, test_case):
        """Log response details for analysis"""
        timestamp = datetime.now().isoformat()
        response_time = response.elapsed.total_seconds() * 1000
        success = response.status_code == 200 and ('token' in response.json() if test_case == 'valid' else True)

        events.request.fire(
            request_type="POST",
            name=f"login_{test_case}",
            response_time=response_time,
            response_length=len(response.content),
            response=response,
            context=self.environment,
            exception=None if success else Exception("Login failed")
        )

    @task(60)  # Higher weight for main login flow
    def test_valid_login(self):
        """Test login with valid credentials"""
        user = random.choice(self.valid_users)
        with self.client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "userName": "",
                    "email": user["email"],
                    "password": user["password"]
                },
                headers=self.headers,
                catch_response=True
        ) as response:
            try:
                if response.status_code == 200:
                    response_data = response.json()
                    if 'token' in response_data:
                        response.success()
                        self.log_response(response, 'valid')
                    else:
                        response.failure(f"Login failed: {response_data.get('msg')}")
                else:
                    response.failure(f"HTTP {response.status_code}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")

    @task(20)  # Lower weight for invalid login attempts
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        user = random.choice(self.invalid_users)
        with self.client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "userName": "",
                    "email": user["email"],
                    "password": user["password"]
                },
                headers=self.headers,
                catch_response=True
        ) as response:
            try:
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('msg') == 'In correct email or password':
                        response.success()
                        self.log_response(response, 'invalid')
                    else:
                        response.failure(f"Unexpected response for invalid login: {response_data}")
                else:
                    response.failure(f"HTTP {response.status_code}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")

    @task(10)  # Lower weight for special character tests
    def test_special_characters_login(self):
        """Test login with special characters in credentials"""
        user = random.choice(self.special_users)
        with self.client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "userName": "",
                    "email": user["email"],
                    "password": user["password"]
                },
                headers=self.headers,
                catch_response=True
        ) as response:
            self.log_response(response, 'special')
            try:
                response_data = response.json()
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"Special characters login failed: {response_data}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")

    @task(5)  # Lowest weight for concurrent login attempts
    def test_concurrent_login(self):
        """Test multiple login attempts with same credentials"""
        user = random.choice(self.valid_users)
        for _ in range(3):  # Try 3 concurrent logins
            with self.client.post(
                    TestConfig.LOGIN_ENDPOINT,
                    data={
                        "userName": "",
                        "email": user["email"],
                        "password": user["password"]
                    },
                    headers=self.headers,
                    catch_response=True,
                    name="concurrent_login"
            ) as response:
                self.log_response(response, 'concurrent')
                try:
                    if response.status_code == 200:
                        response_data = response.json()
                        if 'token' in response_data:
                            response.success()
                        else:
                            response.failure(f"Concurrent login failed: {response_data}")
                    else:
                        response.failure(f"HTTP {response.status_code}")
                except Exception as e:
                    response.failure(f"Failed to parse response: {str(e)}")
                time.sleep(0.1)  # Small delay between concurrent requests

    @task(5)
    def test_username_login(self):
        """Test login with username instead of email"""
        with self.client.post(
                TestConfig.LOGIN_ENDPOINT,
                data={
                    "userName": f"testuser{random.randint(1, 100)}",
                    "email": "",
                    "password": "password123"
                },
                headers=self.headers,
                catch_response=True
        ) as response:
            self.log_response(response, 'username')
            try:
                response_data = response.json()
                if response.status_code == 200:
                    if 'token' in response_data or response_data.get('msg') == 'In correct username or password':
                        response.success()
                    else:
                        response.failure(f"Unexpected response for username login: {response_data}")
                else:
                    response.failure(f"HTTP {response.status_code}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")
