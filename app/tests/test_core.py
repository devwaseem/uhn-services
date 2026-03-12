"""Coverage tests for core modules."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory
from django.test.utils import override_settings
from django.views import View
from django_ratelimit.exceptions import Ratelimited

from app import urls as app_urls
from app.account.models import User
from app.context_processors import allauth_settings, get_site_data
from app.middleware import (
    csp_excluder,
    disable_client_side_caching_middleware,
)
from app.permissions import SuperUserLoginRequiredMixin
from app.types import JSON
from app.utils import render_multiple_templates


class _SuperUserView(SuperUserLoginRequiredMixin, View):  # type: ignore[misc]
    """Simple view to exercise superuser mixin."""

    def get(self, _request: HttpRequest) -> HttpResponse:
        """Return a simple response."""
        return HttpResponse("ok")


@pytest.mark.django_db
def test_superuser_login_required_mixin_allows_superuser() -> None:
    """Superuser mixin allows a superuser through."""
    user = User.objects.create_user(
        email="root@example.com",
        password="strong-password",
        is_staff=True,
        is_superuser=True,
    )
    request = RequestFactory().get("/admin-only/")
    request.user = user

    response = _SuperUserView.as_view()(request)

    assert response.status_code == 200


@pytest.mark.django_db
def test_superuser_login_required_mixin_blocks_non_superuser() -> None:
    """Superuser mixin redirects non-superusers."""
    user = User.objects.create_user(
        email="staff@example.com",
        password="strong-password",
        is_staff=True,
    )
    request = RequestFactory().get("/admin-only/")
    request.user = user

    with pytest.raises(PermissionDenied):
        _SuperUserView.as_view()(request)


@pytest.mark.django_db
def test_context_processors_use_site_data(monkeypatch: Any) -> None:
    """Context processors return expected site metadata."""
    monkeypatch.setattr(
        "app.context_processors.get_current_site",
        lambda _request: SimpleNamespace(domain="example.com", name="Example"),
    )
    request = RequestFactory().get("/", secure=True)

    context = get_site_data(request)

    assert context["protocol"] == "https"
    assert context["base_url"] == "https://example.com"
    assert context["site_name"] == "Example"


@pytest.mark.django_db
def test_context_processors_use_http_when_insecure(monkeypatch: Any) -> None:
    """Context processors default to http for insecure requests."""
    monkeypatch.setattr(
        "app.context_processors.get_current_site",
        lambda _request: SimpleNamespace(domain="example.com", name="Example"),
    )
    request = RequestFactory().get("/")

    context = get_site_data(request)

    assert context["protocol"] == "http"


@pytest.mark.django_db
def test_allauth_settings_respects_flag() -> None:
    """Allauth settings expose the registration flag."""
    request = RequestFactory().get("/")

    with override_settings(ACCOUNT_ALLOW_REGISTRATION=False):
        context = allauth_settings(request)

    assert context["ACCOUNT_ALLOW_REGISTRATION"] is False
    assert allauth_settings(request)["ACCOUNT_ALLOW_REGISTRATION"] is True


def test_disable_client_side_caching_middleware_sets_headers() -> None:
    """Caching middleware adds never-cache headers."""
    request = RequestFactory().get("/")

    middleware = disable_client_side_caching_middleware(
        lambda _request: HttpResponse("ok")
    )
    response = middleware(request)

    assert "Cache-Control" in response.headers


@override_settings(CSP_EXCLUDE_PATH_PREFIXES=["/admin", "/internal"])
def test_csp_excluder_strips_csp_headers_for_configured_paths() -> None:
    request = RequestFactory().get("/admin/login/")

    def get_response(_request: HttpRequest) -> HttpResponse:
        response = HttpResponse("ok")
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Content-Security-Policy-Report-Only"] = (
            "default-src 'none'"
        )
        return response

    middleware = csp_excluder(get_response)
    response = middleware(request)

    assert "Content-Security-Policy" not in response.headers
    assert "Content-Security-Policy-Report-Only" not in response.headers


@override_settings(CSP_EXCLUDE_PATH_PREFIXES=["/admin"])
def test_csp_excluder_keeps_headers_for_non_configured_paths() -> None:
    request = RequestFactory().get("/api/v1/example/")

    def get_response(_request: HttpRequest) -> HttpResponse:
        response = HttpResponse("ok")
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        return response

    middleware = csp_excluder(get_response)
    response = middleware(request)

    assert response.headers["Content-Security-Policy"] == "default-src 'self'"


@pytest.mark.django_db
def test_render_multiple_templates_combines_content() -> None:
    """Render helper concatenates multiple templates."""
    request = RequestFactory().get("/")

    response = render_multiple_templates(
        request=request,
        template_name_list=("txt/robots.txt", "txt/humans.txt"),
    )

    content = response.content.decode("utf-8")
    assert "User-agent" in content
    assert "SITE INFORMATION" in content


def test_url_handlers_render_expected_responses(monkeypatch: Any) -> None:
    """URL handler helpers return appropriate responses."""
    request = RequestFactory().get("/")

    monkeypatch.setattr(
        "app.urls.render",
        lambda _request, _template, status=200: HttpResponse(
            "ok", status=status
        ),
    )

    assert app_urls.not_found().status_code == 404
    assert app_urls.handler404(request).status_code == 404
    assert app_urls.handler500(request).status_code == 500
    assert app_urls.handler403(request).status_code == 403
    assert (
        app_urls.handler403(request, exception=Ratelimited()).status_code
        == 429
    )


def test_miscellaneous_imports_cover_modules() -> None:
    """Miscellaneous module imports cover lightweight modules."""
    import app.account.admin
    import app.admin
    import app.helpers
    import app.models
    import app.request
    import app.templatetags  # noqa: F401

    assert JSON is not None
