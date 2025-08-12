from locust import HttpUser, between, task
from load_tests.utils.utils import signup_payload, login_payload, update_payload, auth_headers


class UpdateUserDataTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        signup_data, password = signup_payload()
        self.user_email = signup_data["email"]
        self.user_password = password

        with self.client.post(
            "/api/users/signup",
            json=signup_data,
            catch_response=True
        ) as response:
            if response.status_code != 201:
                response.failure(
                    f"Signup before updating user data failed: {response.status_code} - {response.text}"
                )
                self.token = None
                return
            else:
                response.success()

        with self.client.post(
            "/api/users/login",
            json=login_payload(self.user_email, self.user_password),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.token = response.json().get("token")
                response.success()
            else:
                response.failure(
                    f"Login before updating user data failed: {response.status_code} - {response.text}"
                )
                self.token = None

    @task
    def update_user_data(self):
        if not self.token:
            return 

        with self.client.put(
            "/api/users/update-data",
            json=update_payload(),
            headers=auth_headers(self.token),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(
                    f"Update user data failed: {response.status_code} - {response.text}"
                )
