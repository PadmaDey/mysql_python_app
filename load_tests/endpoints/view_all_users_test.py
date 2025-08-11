from locust import task
from load_tests.utils.utils import signup_and_login, auth_headers


class ViewAllUsersMixin:
    """
    Mixin to test the 'view all users' endpoint.
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
                    name="view_all_users_setup",
                    response_time=0,
                    response_lenght=0,
                    exception=e
                )

    @task
    def view_all_users(self):
        if not hasattr(self, "token"):
            return  # Skip if login failed in on_start

        with self.client.get("/api/users/", headers=auth_headers(self.token), catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"View all users failed: {response.status_code} - {response.text}")
