from locust import task
from load_tests.utils.utils import signup_payload, login_payload, auth_headers


class ViewAllUsersMixin:
    """
    Mixin to test the 'view all users' endpoint.
    Ensures a fresh authenticated user is created before making requests.
    """

    def on_start(self):
        # 1. Sign up a random valid user
        signup_data, password = signup_payload()
        with self.client.post("/api/users/signup", json=signup_data, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(f"Signup failed before view_all_users: {response.status_code} - {response.text}")
                return
            response.success()

        # 2. Log in to retrieve token
        with self.client.post("/api/users/login", json=login_payload(signup_data["email"], password), catch_response=True) as login_res:
            if login_res.status_code == 200:
                self.token = login_res.json().get("token")
                login_res.success()
            else:
                login_res.failure(f"Login failed before view_all_users: {login_res.status_code} - {login_res.text}")

    @task
    def view_all_users(self):
        if not hasattr(self, "token"):
            return  # Skip if login failed in on_start

        with self.client.get("/api/users/", headers=auth_headers(self.token), catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"View all users failed: {response.status_code} - {response.text}")
