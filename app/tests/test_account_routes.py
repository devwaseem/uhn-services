from __future__ import annotations

from django.urls import resolve, reverse

from app.account.views import (
    AccountLoginView,
    AccountLogoutView,
    AccountResetPasswordDoneView,
    AccountResetPasswordFromKeyDoneView,
    AccountResetPasswordFromKeyView,
    AccountResetPasswordView,
    AccountSignupView,
)


def test_auth_routes_resolve_to_custom_views() -> None:
    """Auth routes use custom frontend-kit account views."""
    cases = [
        ("account_login", reverse("account_login"), AccountLoginView),
        ("account_logout", reverse("account_logout"), AccountLogoutView),
        ("account_signup", reverse("account_signup"), AccountSignupView),
        (
            "account_reset_password",
            reverse("account_reset_password"),
            AccountResetPasswordView,
        ),
        (
            "account_reset_password_done",
            reverse("account_reset_password_done"),
            AccountResetPasswordDoneView,
        ),
        (
            "account_reset_password_from_key",
            reverse(
                "account_reset_password_from_key",
                kwargs={"uidb36": "abc", "key": "token"},
            ),
            AccountResetPasswordFromKeyView,
        ),
        (
            "account_reset_password_from_key_done",
            reverse("account_reset_password_from_key_done"),
            AccountResetPasswordFromKeyDoneView,
        ),
    ]

    for route_name, path, view_class in cases:
        match = resolve(path)
        assert match.view_name == route_name
        assert getattr(match.func, "view_class", None) is view_class
