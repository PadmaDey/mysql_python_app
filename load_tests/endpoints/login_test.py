from locust import task
from load_tests.utils.utils import login_payload, signup_payload


class LoginUserMixin:
    """
    Mixin to test the login endpoint.
    Creates a fresh user during on_start to ensure valid credentials.
    """

    def on_start(self):
        # Create a new user for this Locust user
        signup_data, password = signup_payload()
        self.user_email = signup_data["email"]
        self.user_password = password

        with self.client.post("/api/users/signup", json=signup_data, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(f"Signup before login failed: {response.status_code} - {response.text}")
            else:
                response.success()

    @task
    def login_user(self):
        with self.client.post(
            "/api/users/login",
            json=login_payload(self.user_email, self.user_password),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.token = response.json().get("token")
                response.success()
            else:
                response.failure(f"Login failed: {response.status_code} - {response.text}")
