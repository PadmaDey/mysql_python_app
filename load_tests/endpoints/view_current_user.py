from locust import task
from load_tests.utils.utils import signup_and_login, auth_headers


class ViewCurrentUserMixin:
    """
    Mixin to test the 'view current user' endpoint.
    Signs up and logs in a fresh user on start to ensure a valid token.
    """

    def on_start(self):
        """Signup a random user and log them in before running the test"""
        try:
            self.token = signup_and_login(self.client)
        except RuntimeError as e:
            self.token = None
            if hasattr(self.environment, "events"):
                self.environment.events.request_failure.fire(
                    request_type='SETUP',
                    name="view_current_user_setup",
                    response_time=0,
                    response_length=0,
                    exception=e
                )

    @task
    def view_current_user(self):
        if not hasattr(self, "token"):
            return  # Skip if login failed in on_start

        with self.client.get("/api/users/me", headers=auth_headers(self.token), catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"View current user failed: {response.status_code} - {response.text}")
