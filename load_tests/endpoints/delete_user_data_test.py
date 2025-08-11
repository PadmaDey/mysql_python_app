from locust import task
from load_tests.utils.utils import signup_and_login, auth_headers


class DeleteUserDataMixin:
    """
    Mixin to test the 'delete user data' endpoint.
    Creates and logs in a fresh user before performing delete.
    """

    def on_start(self):
        """Sign up a random user and log them in before running the test."""
        try:
            self.token = signup_and_login(self.client)
        except RuntimeError as e:
            self.token = None
            if hasattr(self.environment, "events"):
                # Record setup failure in Locust's stats
                self.environment.events.request_failure.fire(
                    request_type="SETUP",
                    name="delete_user_data_setup",
                    response_time=0,
                    response_length=0,
                    exception=e,
                )

    @task
    def delete_user_data(self):
        """Send DELETE request to remove user data."""
        if not self.token:
            return  # Skip if setup failed

        with self.client.delete(
            "/api/users/delete-data",
            headers=auth_headers(self.token),
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Delete user data failed: {response.status_code} - {response.text}")
