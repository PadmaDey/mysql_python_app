from locust import HttpUser, between

# Import mixins for individual endpoint tests
from load_tests.endpoints.signup_test import SignupUserMixin
from load_tests.endpoints.login_test import LoginUserMixin
from load_tests.endpoints.view_current_user import ViewCurrentUserMixin
from load_tests.endpoints.view_all_users_test import ViewAllUsersMixin
from load_tests.endpoints.update_user_data_test import UpdateUserDataMixin
from load_tests.endpoints.delete_user_data_test import DeleteUserDataMixin
from load_tests.endpoints.logout_test import LogoutUserMixin


class SignupUserTest(SignupUserMixin, HttpUser):
    wait_time = between(1, 3)


class LoginUserTest(LoginUserMixin, HttpUser):
    wait_time = between(1, 3)


class ViewCurrentUserTest(ViewCurrentUserMixin, HttpUser):
    wait_time = between(1, 3)


class ViewAllUsersTest(ViewAllUsersMixin, HttpUser):
    wait_time = between(1, 3)


class UpdateUserDataTest(UpdateUserDataMixin, HttpUser):
    wait_time = between(1, 3)


class DeleteUserDataTest(DeleteUserDataMixin, HttpUser):
    wait_time = between(1, 3)


class LogoutUserTest(LogoutUserMixin, HttpUser):
    wait_time = between(1, 3)
