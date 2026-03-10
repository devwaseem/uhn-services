from django.urls import path, re_path

from app.account.views import (
    AccountLoginView,
    AccountLogoutView,
    AccountResetPasswordDoneView,
    AccountResetPasswordFromKeyDoneView,
    AccountResetPasswordFromKeyView,
    AccountResetPasswordView,
    AccountSignupView,
)

urlpatterns = [
    path("login/", AccountLoginView.as_view(), name="account_login"),
    path("logout/", AccountLogoutView.as_view(), name="account_logout"),
    path("register/", AccountSignupView.as_view(), name="account_signup"),
    path(
        "password/reset/",
        AccountResetPasswordView.as_view(),
        name="account_reset_password",
    ),
    path(
        "password/reset/done/",
        AccountResetPasswordDoneView.as_view(),
        name="account_reset_password_done",
    ),
    re_path(
        r"^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        AccountResetPasswordFromKeyView.as_view(),
        name="account_reset_password_from_key",
    ),
    path(
        "password/reset/key/done/",
        AccountResetPasswordFromKeyDoneView.as_view(),
        name="account_reset_password_from_key_done",
    ),
]
