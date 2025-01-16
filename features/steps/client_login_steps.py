from behave import given, when, then
import requests
from faker import Faker
import jwt
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

fake = Faker()
BASE_URL = "http://127.0.0.1:5000"


class DataGenerator:
    @staticmethod
    def generate_user_data():
        return {
            "fullName": fake.name(),
            "userName": fake.user_name(),
            "email": fake.email(),
            "password": fake.password(length=12),
            "phone": fake.phone_number()
        }


class LoginClient:
    @staticmethod
    def register_user(user_data):
        response = requests.post(
            f"{BASE_URL}/client_registeration",
            data=user_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response

    @staticmethod
    def login_user(user_data, use_email=True):
        login_data = {
            'userName': '' if use_email else user_data['userName'],
            'email': user_data['email'] if use_email else '',
            'password': user_data['password']
        }
        response = requests.post(
            f"{BASE_URL}/client_login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        return response

    @staticmethod
    def perform_concurrent_logins(users, max_workers=10):
        """
        Perform concurrent login attempts for multiple users
        Returns: List of (user_data, response, duration) tuples
        """
        results = []
        with ThreadPoolExecutor(max_workers=min(len(users), max_workers)) as executor:
            future_to_user = {}
            start_times = {}

            for user_data in users:
                future = executor.submit(LoginClient.login_user, user_data)
                future_to_user[future] = user_data
                start_times[future] = time.time()

            for future in as_completed(future_to_user):
                user_data = future_to_user[future]
                duration = time.time() - start_times[future]
                try:
                    response = future.result()
                    results.append((user_data, response, duration))
                except Exception as e:
                    print(f"Login failed for user {user_data['email']}: {str(e)}")
                    results.append((user_data, None, duration))

        return results


@given("I have a registered user with valid credentials")
def step_impl(context):
    context.registration_payload = DataGenerator.generate_user_data()
    print("Generated valid payload:", context.registration_payload)
    context.credentials = context.registration_payload

    context.response = LoginClient.register_user(context.registration_payload)
    print("Registration response:", context.response.text)


@given('I am a registered user')
def register_test_user(context):
    context.user_data = DataGenerator.generate_user_data()
    response = LoginClient.register_user(context.user_data)
    assert response.json()['msg'] == 'User Registered'


@when('I send a POST request to "/client_login" with the valid credentials')
def login_with_credentials(context):
    context.response = LoginClient.login_user(context.credentials)
    print("Login response:", context.response.text)


@when('I login with valid email')
def login_with_email(context):
    context.response = LoginClient.login_user(context.user_data, use_email=True)


@when('I login with valid username')
def login_with_username(context):
    context.response = LoginClient.login_user(context.user_data, use_email=False)


@when('I attempt to login with incorrect credentials')
def login_with_invalid_credentials(context):
    """Handle invalid login attempts"""
    base_data = context.user_data if hasattr(context, 'user_data') else context.credentials
    invalid_data = base_data.copy()
    invalid_data['password'] = 'wrong_password_123!'

    context.response = LoginClient.login_user(invalid_data)
    print(f"Invalid login attempt response: {context.response.text}")


@then('I should receive a valid JWT token')
def verify_jwt_token_and_contents(context):
    response_json = context.response.json()
    assert "token" in response_json, "Authentication response missing token"
    context.token = response_json["token"]

    # Verify token contents
    secret = '123456'
    decoded = jwt.decode(context.token, secret, algorithms=['HS256'])
    user_info = context.user_data if hasattr(context, 'user_data') else context.credentials

    assert decoded['email'] == user_info['email']
    assert decoded['userName'] == user_info['userName']
    print("Authentication token verified:", context.token)


@then('I should receive an authentication error')
def verify_authentication_error(context):
    response_json = context.response.json()
    assert 'token' not in response_json, "Unexpected token in error response"
    assert response_json.get('msg') in ['Invalid Password', 'Login Failed', 'Authentication Failed'], \
        f"Unexpected error message: {response_json.get('msg')}"
    print(f"Authentication error verified: {response_json.get('msg')}")


@given('I register "{count:d}" test users')
def register_multiple_users(context, count):
    """Register multiple test users using ThreadPoolExecutor"""
    context.test_users = []
    user_data_list = [DataGenerator.generate_user_data() for _ in range(count)]

    with ThreadPoolExecutor(max_workers=min(count, 10)) as executor:
        future_to_user = {
            executor.submit(LoginClient.register_user, user_data): user_data
            for user_data in user_data_list
        }

        for future in as_completed(future_to_user):
            user_data = future_to_user[future]
            try:
                response = future.result()
                assert response.json()['msg'] == 'User Registered'
                context.test_users.append(user_data)
            except Exception as e:
                print(f"User registration failed: {str(e)}")

    print(f"Successfully registered {len(context.test_users)} users")


@when('I test concurrent user logins')
def test_concurrent_logins(context):
    """Execute and measure concurrent login attempts"""
    assert hasattr(context, 'test_users'), "No test users available for concurrent login test"

    # Perform concurrent logins and store results
    context.start_time = time.time()
    context.login_results = LoginClient.perform_concurrent_logins(context.test_users)
    context.total_duration = time.time() - context.start_time

    # Process and store metrics
    context.successful_logins = sum(
        1 for _, response, _ in context.login_results if response and 'token' in response.json())
    context.failed_logins = len(context.login_results) - context.successful_logins
    context.avg_response_time = sum(duration for _, _, duration in context.login_results) / len(context.login_results)
    context.max_response_time = max(duration for _, _, duration in context.login_results)

    print(f"\nConcurrent Login Test Results ({datetime.now()}):")
    print(f"Total Users: {len(context.login_results)}")
    print(f"Successful Logins: {context.successful_logins}")
    print(f"Failed Logins: {context.failed_logins}")
    print(f"Total Duration: {context.total_duration:.2f}s")
    print(f"Average Response Time: {context.avg_response_time:.3f}s")
    print(f"Max Response Time: {context.max_response_time:.3f}s")


@then('all login requests should succeed with valid tokens')
def verify_concurrent_logins(context):
    """Verify all concurrent login attempts were successful"""
    assert hasattr(context, 'login_results'), "No login results available to verify"

    # Verify each login attempt
    failed_logins = []
    for user_data, response, duration in context.login_results:
        try:
            assert response is not None, "No response received"
            response_json = response.json()
            assert "token" in response_json, "No token in response"

            # Verify token contents
            token = response_json["token"]
            decoded = jwt.decode(token, '123456', algorithms=['HS256'])
            assert decoded['email'] == user_data['email'], "Email mismatch in token"
            assert decoded['userName'] == user_data['userName'], "Username mismatch in token"
        except Exception as e:
            failed_logins.append((user_data['email'], str(e)))

    # Report results
    if failed_logins:
        failure_details = "\n".join(f"- {email}: {error}" for email, error in failed_logins)
        raise AssertionError(f"Login verification failed for {len(failed_logins)} users:\n{failure_details}")

    print(f"\nSuccessfully verified {len(context.login_results)} concurrent logins")
    print(f"Performance Metrics:")
    print(f"- Average response time: {context.avg_response_time:.3f}s")
    print(f"- Maximum response time: {context.max_response_time:.3f}s")
    print(f"- Total test duration: {context.total_duration:.2f}s")