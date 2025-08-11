from locust import task
from load_tests.utils.utils import signup_payload


class SignupUserMixin:
    """
    Mixin to perform the signup API call during a Locust test.
    Generates a new random user each time to avoid duplicate constraint errors.
    """

    @task
    def signup_user(self):
        # Generate a random signup payload
        payload, _ = signup_payload()

        with self.client.post("/api/users/signup", json=payload, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(f"Signup failed: {response.status_code} - {response.text}")
            else:
                response.success()
