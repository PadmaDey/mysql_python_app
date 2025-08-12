from locust import HttpUser, between, task
from load_tests.utils.utils import (
    signup_payload,
    login_payload,
    update_payload,
    auth_headers
)


class BaseUserTest(HttpUser):
    """
    Base class providing reusable signup + login for each API test.
    Ensures each call uses a completely fresh account/session.
    """
    abstract = True
    wait_time = between(1, 3)

    def signup_and_login(self):
        """Creates a new user, logs in, returns (email, password, token)."""
        signup_data, password = signup_payload()
        email = signup_data["email"]

        # Signup
        with self.client.post("/api/users/signup", json=signup_data, catch_response=True) as resp:
            if resp.status_code != 201:
                resp.failure(f"Signup failed: {resp.status_code} - {resp.text}")
                return None, None, None
            resp.success()

        # Login
        with self.client.post(
            "/api/users/login",
            json=login_payload(email, password),
            catch_response=True
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Login failed: {resp.status_code} - {resp.text}")
                return None, None, None
            token = resp.json().get("token")
            resp.success()

        return email, password, token


class SignupUserTest(HttpUser):
    """Load test for user signup endpoint."""
    wait_time = between(1, 3)

    @task
    def signup_user(self):
        payload, _ = signup_payload()
        with self.client.post("/api/users/signup", json=payload, catch_response=True) as resp:
            if resp.status_code != 201:
                resp.failure(f"Signup failed: {resp.status_code} - {resp.text}")
            else:
                resp.success()


class LoginUserTest(BaseUserTest):
    """Load test for user login endpoint."""
    @task
    def login_user(self):
        email, password, _ = self.signup_and_login()
        if not email or not password:
            return
        with self.client.post(
            "/api/users/login",
            json=login_payload(email, password),
            catch_response=True
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Login failed: {resp.status_code} - {resp.text}")


class ViewCurrentUserTest(BaseUserTest):
    @task
    def view_current_user(self):
        _, _, token = self.signup_and_login()
        if not token:
            return
        with self.client.get("/api/users/me", headers=auth_headers(token), catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"View current user failed: {resp.status_code} - {resp.text}")


class ViewAllUsersTest(BaseUserTest):
    @task
    def view_all_users(self):
        _, _, token = self.signup_and_login()
        if not token:
            return
        with self.client.get("/api/users/", headers=auth_headers(token), catch_response=True) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"View all users failed: {resp.status_code} - {resp.text}")


class UpdateUserDataTest(BaseUserTest):
    @task
    def update_user_data(self):
        _, _, token = self.signup_and_login()
        if not token:
            return
        with self.client.put(
            "/api/users/update-data",
            json=update_payload(),
            headers=auth_headers(token),
            catch_response=True
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Update user data failed: {resp.status_code} - {resp.text}")


class LogoutUserTest(BaseUserTest):
    @task
    def logout_user(self):
        _, _, token = self.signup_and_login()
        if not token:
            return
        with self.client.post(
            "/api/users/log-out",
            headers=auth_headers(token),
            catch_response=True
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Logout failed: {resp.status_code} - {resp.text}")


class DeleteUserDataTest(BaseUserTest):
    @task
    def delete_user_data(self):
        _, _, token = self.signup_and_login()
        if not token:
            return
        with self.client.delete(
            "/api/users/delete-data",
            headers=auth_headers(token),
            catch_response=True
        ) as resp:
            if resp.status_code == 200:
                resp.success()
            else:
                resp.failure(f"Delete user data failed: {resp.status_code} - {resp.text}")
