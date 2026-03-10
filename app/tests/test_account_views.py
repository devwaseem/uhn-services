from __future__ import annotations

import pytest
from django.test import Client
from django.test.utils import override_settings
from django.urls import reverse

from app.account.models import User


@pytest.mark.django_db
def test_signup_page_renders(client: Client) -> None:
    response = client.get(reverse("account_signup"))

    assert response.status_code == 200
    assert "Create account" in response.content.decode()


@pytest.mark.django_db
def test_signup_post_creates_user(client: Client) -> None:
    response = client.post(
        reverse("account_signup"),
        data={
            "email": "new-user@example.com",
            "password1": "StrongTestPassword123!",
            "password2": "StrongTestPassword123!",
        },
    )

    assert response.status_code == 302
    assert User.objects.filter(email="new-user@example.com").exists()


@pytest.mark.django_db
def test_password_reset_page_renders(client: Client) -> None:
    """Password reset page renders successfully."""
    url = reverse("account_reset_password")
    response = client.get(url)
    assert response.status_code == 200
    assert "Reset password" in response.content.decode()


@pytest.mark.django_db
def test_password_reset_done_page_renders(client: Client) -> None:
    """Password reset done page renders successfully."""
    url = reverse("account_reset_password_done")
    response = client.get(url)
    assert response.status_code == 200
    assert "Check your email" in response.content.decode()


@pytest.mark.django_db
def test_password_reset_from_key_page_renders_invalid_token(
    client: Client,
) -> None:
    """Password reset from key page renders with invalid token message."""
    url = reverse(
        "account_reset_password_from_key",
        kwargs={"uidb36": "invalid", "key": "token"},
    )
    response = client.get(url)
    assert response.status_code == 200
    assert "reset link is invalid" in response.content.decode()


@pytest.mark.django_db
def test_password_reset_from_key_done_page_renders(client: Client) -> None:
    """Password reset from key done page renders successfully."""
    url = reverse("account_reset_password_from_key_done")
    response = client.get(url)
    assert response.status_code == 200
    assert "Password updated" in response.content.decode()


@pytest.mark.django_db
def test_password_reset_post_redirects_to_done(client: Client) -> None:
    """Password reset POST completes without backend errors."""
    user = User.objects.create(email="reset@example.com")
    user.set_password("strong-password")
    user.save(update_fields=["password"])
    url = reverse("account_reset_password")
    response = client.post(url, data={"email": user.email})
    assert response.status_code == 302
    assert response.headers["Location"] == reverse(
        "account_reset_password_done"
    )


@pytest.mark.django_db
def test_login_page_redirects_authenticated_user(client: Client) -> None:
    user = User.objects.create(email="viewer@example.com")
    user.set_password("strong-password")
    user.save(update_fields=["password"])
    client.force_login(user)

    response = client.get(reverse("account_login"))

    assert response.status_code == 302
    assert response.headers["Location"] == "/"


@pytest.mark.django_db
def test_login_post_redirects_to_login_redirect_url(client: Client) -> None:
    user = User.objects.create(email="signin@example.com")
    user.set_password("strong-password")
    user.save(update_fields=["password"])

    with override_settings(LOGIN_REDIRECT_URL="/"):
        response = client.post(
            reverse("account_login"),
            data={
                "login": user.email,
                "password": "strong-password",
            },
        )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
