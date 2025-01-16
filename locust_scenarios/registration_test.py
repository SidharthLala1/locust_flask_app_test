from locust import HttpUser, task, between, events
from faker import Faker
import json
import random
import sys
import os
from datetime import datetime
import string

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.test_config import TestConfig

fake = Faker()


class UserRegistration(HttpUser):
    host = "http://127.0.0.1:5000"
    wait_time = between(TestConfig.MIN_WAIT_TIME // 1000, TestConfig.MAX_WAIT_TIME // 1000)

    def on_start(self):
        """Initialize test data sets"""
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.valid_users = []
        # Pre-generate some users for duplicate testing
        for _ in range(5):
            self.valid_users.append(self.generate_valid_user_data())

    def generate_valid_user_data(self):
        """Generate valid user data"""
        return {
            "fullName": fake.name(),
            "userName": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(length=12, special_chars=True, digits=True,
                                      upper_case=True, lower_case=True),
            "phone": fake.numerify('##########')  # 10 digit phone number
        }

    def generate_invalid_user_data(self):
        """Generate various invalid user data scenarios"""
        scenarios = [
            # Empty fields
            {
                "fullName": "",
                "userName": "",
                "email": "",
                "password": "",
                "phone": ""
            },
            # Invalid email formats
            {
                "fullName": fake.name(),
                "userName": fake.user_name(),
                "email": "invalid.email",
                "password": fake.password(),
                "phone": fake.numerify('##########')
            },
            # Very long inputs
            {
                "fullName": "A" * 256,
                "userName": "U" * 128,
                "email": "a" * 200 + "@test.com",
                "password": "P" * 128,
                "phone": "1" * 20
            },
            # Special characters in fields
            {
                "fullName": "Test User !@#$%",
                "userName": "test_user@123",
                "email": "test+user@example.com",
                "password": "pass!@#$%^&*()",
                "phone": "+1-234-567-8900"
            },
            # Unicode characters
            {
                "fullName": "测试用户",
                "userName": "测试",
                "email": "test@example.com",
                "password": "パスワード123",
                "phone": "1234567890"
            }
        ]
        return random.choice(scenarios)

    def log_test_result(self, response, test_case):
        """Log detailed test results"""
        timestamp = datetime.now().isoformat()
        response_time = response.elapsed.total_seconds() * 1000

        events.request.fire(
            request_type="POST",
            name=f"registration_{test_case}",
            response_time=response_time,
            response_length=len(response.content),
            response=response,
            context=self.environment
        )

    @task(40)
    def test_valid_registration(self):
        """Test registration with valid data"""
        with self.client.post(
                "/client_registeration",
                data=self.generate_valid_user_data(),
                headers=self.headers,
                catch_response=True
        ) as response:
            try:
                if response.status_code == 200:
                    response_data = response.json()
                    if response_data.get('msg') == 'User Registered':
                        response.success()
                        self.log_test_result(response, 'valid')
                    else:
                        response.failure(f"Registration failed: {response_data.get('msg')}")
                else:
                    response.failure(f"HTTP {response.status_code}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")

    @task(20)
    def test_duplicate_email_registration(self):
        """Test registration with duplicate email"""
        user_data = random.choice(self.valid_users)
        with self.client.post(
                "/client_registeration",
                data=user_data,
                headers=self.headers,
                catch_response=True
        ) as response:
            try:
                response_data = response.json()
                if response_data.get('msg') == 'Email already Exist':
                    response.success()
                    self.log_test_result(response, 'duplicate')
                else:
                    response.failure(f"Unexpected response for duplicate email: {response_data}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")

    @task(20)
    def test_invalid_registration(self):
        """Test registration with invalid data"""
        with self.client.post(
                "/client_registeration",
                data=self.generate_invalid_user_data(),
                headers=self.headers,
                catch_response=True
        ) as response:
            try:
                response_data = response.json()
                if response_data.get('msg') == 'Invalid Data':
                    response.success()
                    self.log_test_result(response, 'invalid')
                else:
                    response.failure(f"Unexpected response for invalid data: {response_data}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")

    @task(10)
    def test_concurrent_registration(self):
        """Test concurrent registration with same data"""
        user_data = self.generate_valid_user_data()
        for _ in range(3):  # Try 3 concurrent registrations
            with self.client.post(
                    "/client_registeration",
                    data=user_data,
                    headers=self.headers,
                    catch_response=True,
                    name="concurrent_registration"
            ) as response:
                self.log_test_result(response, 'concurrent')
                try:
                    if response.status_code == 200:
                        response.success()
                    else:
                        response.failure(f"HTTP {response.status_code}")
                except Exception as e:
                    response.failure(f"Failed to parse response: {str(e)}")

    @task(10)
    def test_password_variations(self):
        """Test registration with various password formats"""
        user_data = self.generate_valid_user_data()
        password_variations = [
            ''.join(random.choices(string.ascii_letters, k=8)),  # Letters only
            ''.join(random.choices(string.digits, k=8)),  # Numbers only
            ''.join(random.choices(string.punctuation, k=8)),  # Special chars only
            ''.join(random.choices(string.ascii_letters + string.digits, k=16)),  # Alphanumeric
            ''.join(random.choices(string.printable, k=12))  # Mixed characters
        ]

        user_data['password'] = random.choice(password_variations)
        with self.client.post(
                "/client_registeration",
                data=user_data,
                headers=self.headers,
                catch_response=True
        ) as response:
            self.log_test_result(response, 'password_variation')
            try:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"HTTP {response.status_code}")
            except Exception as e:
                response.failure(f"Failed to parse response: {str(e)}")
