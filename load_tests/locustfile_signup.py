from locust import HttpUser, between, task
from load_tests.endpoints.signup_test import SignupUserMixin

class SignupUserTest(SignupUserMixin, HttpUser):
    wait_time = between(1, 3)

    @task
    def sanity_check(self):
        print("SignupUserTest loaded successfully.")
