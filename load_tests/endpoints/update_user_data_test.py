from locust import task
from load_tests.utils.utils import signup_and_login, update_payload, auth_headers


class UpdateUserDataMixin:
    """
    Mixin to test the 'update user data' endpoint.
    Ensures a fresh authenticated user is created before making requests.
    """

    def on_start(self):
        """Sign up a random user and log them in before running the test"""
        try:
            self.token = signup_and_login(self.client)
        except RuntimeError as e:
            self.token = None
            if hasattr(self.environment, "events"):
                self.environment.events.request_failure.fire(
                    request_type="SETUP",
                    name="update_user_data_setup",
                    response_time=0,
                    response_length=0,
                    exception=e
                )

    @task
    def update_user_data(self):
        if not hasattr(self, "token"):
            return  # Skip if login failed

        with self.client.put(
            "/api/users/update-data",
            json=update_payload(),
            headers=auth_headers(self.token),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Update user data failed: {response.status_code} - {response.text}")
