from locust import HttpUser, between, task
from load_tests.utils.utils import (
    signup_payload,
    login_payload,
    update_payload,
    auth_headers
)


class SequentialUserFlow(HttpUser):
    """
    Executes the entire flow sequentially:
    1. Signup
    2. Login
    3. View current user
    4. View all users
    5. Update user data
    6. Logout
    7. Delete user data
    Each step uses a fresh signup+login (isolated session).
    """
    wait_time = between(1, 3)

    @task
    def run_sequential_flow(self):
        # Step 1: Signup
        signup_data, password = signup_payload()
        email = signup_data["email"]
        with self.client.post("/api/users/signup", json=signup_data, catch_response=True) as resp:
            if resp.status_code != 201:
                resp.failure(f"Signup failed: {resp.status_code} - {resp.text}")
                return
            resp.success()

        # Step 2: Login
        with self.client.post("/api/users/login", json=login_payload(email, password), catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Login failed: {resp.status_code} - {resp.text}")
                return
            token = resp.json().get("token")
            resp.success()

        # Step 3: View current user
        with self.client.get("/api/users/me", headers=auth_headers(token), catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"View current user failed: {resp.status_code} - {resp.text}")
                return
            resp.success()

        # Step 4: View all users
        with self.client.get("/api/users/", headers=auth_headers(token), catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"View all users failed: {resp.status_code} - {resp.text}")
                return
            resp.success()

        # Step 5: Update user data
        with self.client.put(
            "/api/users/update-data",
            json=update_payload(),
            headers=auth_headers(token),
            catch_response=True
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Update user data failed: {resp.status_code} - {resp.text}")
                return
            resp.success()

        # Step 6: Logout
        with self.client.post(
            "/api/users/log-out",
            headers=auth_headers(token),
            catch_response=True
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Logout failed: {resp.status_code} - {resp.text}")
                return
            resp.success()

        # Step 7: Delete user data (fresh login to delete after logout)
        with self.client.post("/api/users/login", json=login_payload(email, password), catch_response=True) as resp:
            if resp.status_code != 200:
                resp.failure(f"Re-login for delete failed: {resp.status_code} - {resp.text}")
                return
            delete_token = resp.json().get("token")
            resp.success()

        with self.client.delete(
            "/api/users/delete-data",
            headers=auth_headers(delete_token),
            catch_response=True
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Delete user data failed: {resp.status_code} - {resp.text}")
            else:
                resp.success()
