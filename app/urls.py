from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import render
from django.urls import include, path
from django.views.generic import TemplateView
from django_ratelimit.exceptions import Ratelimited

from app.views.home import HomeView


def not_found() -> HttpResponse:
    return HttpResponseNotFound()


def handler404(
    request: HttpRequest,
    *_args: int | bool | str,
    **_kwargs: int | bool | str,
) -> HttpResponse:
    return render(request, "errors/404.html", status=404)


def handler403(
    request: HttpRequest,
    exception: Exception | None = None,
) -> HttpResponse:
    if isinstance(exception, Ratelimited):
        return HttpResponse("Sorry you are blocked", status=429)
    return render(request, "errors/403.html", status=403)


def handler500(
    request: HttpRequest,
    *_args: int | bool | str,
    **_kwargs: int | bool | str,
) -> HttpResponse:
    return render(request, "errors/500.html", status=500)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("app.account.urls")),
    path("", HomeView.as_view(), name="home"),
    # Text and xml static files:
    path(
        "robots.txt",
        TemplateView.as_view(
            template_name="txt/robots.txt",
            content_type="text/plain",
        ),
    ),
    path(
        "humans.txt",
        TemplateView.as_view(
            template_name="txt/humans.txt",
            content_type="text/plain",
        ),
    ),
    *static(
        prefix=settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    ),
]

if settings.DEBUG:  # pragma: no cover
    import debug_toolbar

    urlpatterns = [
        # Django silk
        # path("silk/", include("silk.urls", namespace="silk")), # noqa
        path("__reload__/", include("django_browser_reload.urls")),
        # URLs specific only to django-debug-toolbar:
        path("__debug__/", include(debug_toolbar.urls)),
        *urlpatterns,
        # Serving media files in development only:
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]

if getattr(settings, "ENABLE_SILK_PROFILING", False):
    urlpatterns += [
        # Django silk
        path("silk/", include("silk.urls", namespace="silk")),
    ]

if getattr(settings, "ENABLE_HEALTH_CHECK", False):
    from health_check.views import HealthCheckView
    from redis import Redis

    redis_check = (
        "health_check.contrib.redis.Redis",
        {"client": Redis.from_url(settings.REDIS_URL)},
    )

    health_checks = [
        "health_check.Cache",
        "health_check.Database",
        "health_check.Disk",
        "health_check.Mail",
        "health_check.Memory",
        "health_check.Storage",
        "health_check.contrib.celery.Ping",
        redis_check,
    ]

    ready_checks = [
        "health_check.Cache",
        "health_check.Database",
        redis_check,
    ]

    urlpatterns += [
        path(
            "healthz/",
            HealthCheckView.as_view(checks=health_checks),
        ),
        path(
            "readyz/",
            HealthCheckView.as_view(checks=ready_checks),
        ),
    ]
