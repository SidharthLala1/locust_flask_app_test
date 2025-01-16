from behave import given, when, then
import requests
from faker import Faker

fake = Faker()
BASE_URL = "http://127.0.0.1:5000"  # Replace with the actual base URL


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



@given("I have a registered user with valid credentials")
def step_impl(context):
    # Generate user data
    # Generate and store the payload in context
    context.registration_payload = DataGenerator.generate_user_data()
    print("Generated valid payload:", context.registration_payload)
    user_data = DataGenerator.generate_user_data()
    context.credentials = {
        "userName": user_data["userName"],
        "password": user_data["password"],
        "fullName":user_data["fullName"],
        "email":user_data["email"],
        "phone":user_data["phone"]
    }

    # Ensure the payload is sent as form data
    context.response = requests.post(
        f"{BASE_URL}/client_registeration",
        data=context.registration_payload, # Send as form data
        headers={"Content-Type": "application/x-www-form-urlencoded"}  # Specify form content
    )
    print("Registration response:", context.response.text)  # Debugging
    #assert context.response.status_code in [200, 201], f"Expected 201, got {context.response.status_code}"



@when("I send a POST request to \"/client_login\" with the valid credentials")
def step_impl(context):
    context.response = requests.post(
        f"{BASE_URL}/client_login",
        data={
            "userName": context.credentials["userName"],
            "password": context.credentials["password"],
            "email":context.credentials["email"]
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    print("Login response:", context.response.text)  # Debugging



@then("the user should be authenticated successfully")
def step_impl(context):
    response_json = context.response.json()
    assert "token" in response_json, "Authentication response missing token"
    print("Authentication token:", response_json["token"])
