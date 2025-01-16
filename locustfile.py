from locust import HttpUser, task, between
from steps.common_steps import register_user, login_user
from faker import Faker
import random

class UserBehavior(HttpUser):
    wait_time = between(1, 3)
    fake = Faker()
    registered_users = []

    @task(3)
    def client_register(self):
        """Stress test client registration."""
        payload = {
            "username": self.fake.user_name(),
            "email": self.fake.email(),
            "password": self.fake.password(length=12),
            "full_name": self.fake.name(),
            "phone": self.fake.phone_number()
        }
        response = register_user(payload)
        if response.status_code == 201:
            self.registered_users.append({"username": payload["username"], "password": payload["password"]})

    @task(2)
    def client_login(self):
        """Stress test client login."""
        if not self.registered_users:
            return
        user = random.choice(self.registered_users)
        credentials = {"username": user["username"], "password": user["password"]}
        response = login_user(credentials)
        assert response.status_code == 200, f"Login failed with status {response.status_code}"
