from locust import task
from load_tests.utils.utils import signup_and_login, auth_headers


class LogoutUserMixin:
    """
    Mixin to test the 'logout' endpoint.
    Creates and logs in a fresh user before performing logout.
    """

    def on_start(self):
        """Sign up a random user and log them in before running the test."""
        try:
            self.token = signup_and_login(self.client)
        except RuntimeError as e:
            self.token = None
            if hasattr(self.environment, "events"):
                self.environment.events.request_failure.fire(
                    request_type="SETUP",
                    name="logout_user_data_setup",
                    response_time=0,
                    response_length=0,
                    exception=e,
                )


    @task
    def logout_user(self):
        if not hasattr(self, "token"):
            return  # Skip if login failed

        with self.client.post(
            "/api/users/log-out",
            headers=auth_headers(self.token),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Logout failed: {response.status_code} - {response.text}")
