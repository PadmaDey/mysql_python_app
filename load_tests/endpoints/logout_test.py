from locust import task
from load_tests.utils.utils import signup_payload, login_payload, auth_headers


class LogoutUserMixin:
    def on_start(self):
        signup_data, password = signup_payload()
        self.user_email = signup_data["email"]
        self.user_password = password

        with self.client.post("/api/users/signup", json=signup_data, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(
                    f"Signup before logout failed: {response.status_code} - {response.text}"
                )
                self.token = None
                return
            else:
                response.success()

        with self.client.post("/api/users/login", json=login_payload(self.user_email, self.user_password), catch_response=True) as response:
            if response.status_code == 200:
                self.token = response.json().get("token")
                response.success()
            else:
                response.failure(
                    f"Login before logout failed: {response.status_code} - {response.text}"
                )
                self.token = None

    @task
    def logout_user(self):
        if not self.token:
            return

        with self.client.post("/api/users/log-out", headers=auth_headers(self.token), catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Logout failed: {response.status_code} - {response.text}"
                )
