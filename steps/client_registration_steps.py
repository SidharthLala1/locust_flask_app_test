from behave import given, when, then
from faker import Faker
import requests

fake = Faker()

BASE_URL = "http://127.0.0.1:5000"  # Replace with your actual base URL


class DataGenerator:
    @staticmethod
    def generate_registration_payload(valid=True):
        if valid:
            return {
                "userName": fake.user_name(),
                "email": fake.email(),
                "password": fake.password(length=12),
                "fullName": fake.name(),
                "phone": fake.phone_number()
            }
        else:
            return {
                "userName": "invaliduser",
                "email": "not-an-email",  # Invalid email
                "password": "password123",
                "fullName": "Invalid",
                "phone": "1234567890"
            }


@given("I have a valid user registration payload")
def step_impl(context):
    # Generate and store the payload in context
    context.registration_payload = DataGenerator.generate_registration_payload(valid=True)
    print("Generated valid payload:", context.registration_payload)


@given("I have a registration payload with an invalid email")
def step_impl(context):
    # Generate and store the payload in context
    context.registration_payload = DataGenerator.generate_registration_payload(valid=False)
    print("Generated invalid payload:", context.registration_payload)


@when("I send a POST request to \"/client_registeration\"")
def step_impl(context):
    assert hasattr(context, 'registration_payload'), "No registration payload found in context"

    # Ensure the payload is sent as form data
    context.response = requests.post(
        f"{BASE_URL}/client_registeration",
        data=context.registration_payload,  # Send as form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}  # Specify form content
    )
    print("Registration response:", context.response.text)  # Debugging


@then("I should receive a 200 response")
def step_impl(context):
    assert context.response.status_code == 200, f"Expected 200, got {context.response.status_code}"


@then("I should receive a 400 response")
def step_impl(context):
    assert context.response.status_code == 400, f"Expected 400, got {context.response.status_code}"


@then("an appropriate error message should be displayed")
def step_impl(context):
    response_json = context.response.json()
    assert "error" in response_json, "Error message missing from response"
    print("Error message:", response_json["error"])


from locust import HttpUser, task, between
from faker import Faker
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvalidEmailRegistrationTest(HttpUser):
    wait_time = between(1, 3)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fake = Faker()

    def generate_invalid_email_payload(self):
        """
        Given I have a registration payload with an invalid email
        Returns registration data with invalid email formats
        """
        invalid_email_formats = [
            "plainaddress",
            "@missingusername.com",
            "username@.com",
            "username@domain..com",
            "username@.domain.com",
            "username@domain",
            "username.@domain.com",
            ".username@domain.com",
            "username#@domain.com",
            "username@domain..com"
        ]

        return {
            "username": self.fake.user_name(),
            "email": self.fake.random_element(invalid_email_formats),
            "password": self.fake.password(length=12),
            "first_name": self.fake.first_name(),
            "last_name": self.fake.last_name(),
            "phone": self.fake.phone_number()
        }

    @task
    def test_invalid_email_registration(self):
        """
        Scenario: Registration with an invalid email
        When I send a POST request to "/client_registeration"
        Then I should receive a 400 response
        And an error message should be displayed
        """
        # Generate payload with invalid email
        payload = self.generate_invalid_email_payload()

        # Send registration request with invalid email
        with self.client.post(
                "/client_registeration",
                json=payload,
                catch_response=True
        ) as response:
            try:
                # Verify response status code is 400
                if response.status_code == 400:
                    # Verify error message exists in response
                    response_data = response.json()
                    if 'error' in response_data and 'email' in response_data['error'].lower():
                        logger.info(f"Successfully validated invalid email rejection for: {payload['email']}")
                        response.success()
                    else:
                        error_msg = "Response did not contain expected email error message"
                        logger.error(error_msg)
                        response.failure(error_msg)
                else:
                    error_msg = f"Expected status code 400, but got {response.status_code}"
                    logger.error(error_msg)
                    response.failure(error_msg)

            except json.JSONDecodeError:
                error_msg = "Failed to parse response JSON"
                logger.error(error_msg)
                response.failure(error_msg)
            except Exception as e:
                logger.error(f"Unexpected error during test: {str(e)}")
                response.failure(str(e))


class LoadTest:
    def __init__(self):
        """Configure test parameters"""
        self.host = "http://your-api-host"  # Replace with actual host
        self.num_users = 10
        self.spawn_rate = 1
        self.test_time = "5m"

    def run(self):
        """Execute load test"""
        import subprocess

        command = [
            "locust",
            "-f", "invalid_email_test.py",
            "--host", self.host,
            "--users", str(self.num_users),
            "--spawn-rate", str(self.spawn_rate),
            "--run-time", self.test_time,
            "--headless",
            "--csv", "invalid_email_test_results",
            "--html", "invalid_email_test_report.html"
        ]

        subprocess.run(command)


if __name__ == "__main__":
    # Run the load test
    load_test = LoadTest()
    load_test.run()