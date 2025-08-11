from locust import task
from load_tests.utils.utils import signup_payload, login_payload, auth_headers


class ViewCurrentUserMixin:
    """
    Mixin to test the 'view current user' endpoint.
    Signs up and logs in a fresh user on start to ensure a valid token.
    """

    def on_start(self):
        # Create a new user
        signup_data, password = signup_payload()
        with self.client.post("/api/users/signup", json=signup_data, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(f"Signup failed before view_current_user: {response.status_code} - {response.text}")
                return
            response.success()

        # Login to get token
        with self.client.post("/api/users/login", json=login_payload(signup_data["email"], password), catch_response=True) as login_res:
            if login_res.status_code == 200:
                self.token = login_res.json().get("token")
                login_res.success()
            else:
                login_res.failure(f"Login failed before view_current_user: {login_res.status_code} - {login_res.text}")

    @task
    def view_current_user(self):
        if not hasattr(self, "token"):
            return  # Skip if login failed in on_start

        with self.client.get("/api/users/me", headers=auth_headers(self.token), catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"View current user failed: {response.status_code} - {response.text}")
