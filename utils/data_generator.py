from faker import Faker
import random


class DataGenerator:
    def __init__(self):
        self.fake = Faker()

    def generate_user_data(self):
        return {
            "fullName": self.fake.name(),
            "userName": self.fake.user_name(),
            "email": self.fake.email(),
            "password": self.fake.password(),
            "phone": self.fake.phone_number()
        }

    def generate_login_data(self):
        return {
            "userName": "",
            "email": self.fake.email(),
            "password": self.fake.password()
        }
