from behave import given, when, then
import requests
import jwt
import threading
import time
from faker import Faker

fake = Faker()

BASE_URL = "http://127.0.0.1:5000"
HEADERS = {"Content-Type": "application/x-www-form-urlencoded"}

# In client_registration_steps.py
@given('I am a newly registered user')  # Changed from 'I am a registered user'
def register_test_user(context):
    context.user_data = {
        'fullName': fake.name(),
        'userName': fake.user_name(),
        'email': fake.email(),
        'password': fake.password(),
        'phone': fake.phone_number()
    }
    response = requests.post(
        f'{BASE_URL}/client_registeration',  # Fixed string formatting
        data=context.user_data,
        headers=HEADERS
    )
    assert response.json()['msg'] == 'User Registered'


@when('I login with valid email and password')
def login_with_email(context):
    login_data = {
        'userName': '',
        'email': context.user_data['email'],
        'password': context.user_data['password']
    }
    context.response = requests.post(
        f'{BASE_URL}/client_login',
        data=login_data,
        headers=HEADERS
    )


@when('I login with valid username and password')
def login_with_username(context):
    login_data = {
        'userName': context.user_data['userName'],
        'email': '',
        'password': context.user_data['password']
    }
    context.response = requests.post(
        f'{BASE_URL}/client_login',
        data=login_data,
        headers=HEADERS
    )


@then('I should receive a JWT token')
def verify_jwt_token(context):
    assert 'token' in context.response.json()
    context.token = context.response.json()['token']


@then('the token should contain correct user information')
def verify_token_contents(context):
    secret = '123456'  # Same as in the application
    decoded = jwt.decode(context.token, secret, algorithms=['HS256'])
    assert decoded['email'] == context.user_data['email']
    assert decoded['userName'] == context.user_data['userName']


@when('I login with incorrect password')
def login_with_wrong_password(context):
    login_data = {
        'userName': '',
        'email': context.user_data['email'],
        'password': 'wrong_password'
    }
    context.response = requests.post(
        f'{BASE_URL}/client_login',
        data=login_data,
        headers=HEADERS
    )


@given('there are "{count}" registered users')
def register_multiple_test_users(context, count):
    context.test_users = []
    for _ in range(int(count)):
        user_data = {
            'fullName': fake.name(),
            'userName': fake.user_name(),
            'email': fake.email(),
            'password': fake.password(),
            'phone': fake.phone_number()
        }
        response = requests.post(
            f'{BASE_URL}/client_registeration',
            data=user_data,
            headers=HEADERS
        )
        assert response.json()['msg'] == 'User Registered'
        context.test_users.append(user_data)


@when('all users attempt to login simultaneously')
def login_multiple_users(context):
    context.start_time = time.time()
    context.responses = []
    threads = []

    def login_user(user_data):
        login_data = {
            'userName': '',
            'email': user_data['email'],
            'password': user_data['password']
        }
        response = requests.post(
            f'{BASE_URL}/client_login',
            data=login_data,
            headers=HEADERS
        )
        context.responses.append(response)

    for user_data in context.test_users:
        thread = threading.Thread(target=login_user, args=(user_data,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


@then('login requests should complete successfully')
def verify_multiple_logins(context):
    duration = time.time() - context.start_time
    successful_logins = sum(
        1 for response in context.responses
        if 'token' in response.json()
    )
    assert successful_logins == len(context.responses)
    print(f"Completed {len(context.responses)} logins in {duration:.2f} seconds")
