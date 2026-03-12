from collections.abc import Awaitable, Callable
from inspect import iscoroutinefunction
from typing import cast, overload

from django.conf import settings
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.utils.cache import add_never_cache_headers


def disable_client_side_caching_middleware(
    get_response: Callable[[HttpRequest], HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    def middleware(request: HttpRequest) -> HttpResponse:
        response = get_response(request)
        add_never_cache_headers(response)
        return response

    return middleware


@overload
def csp_excluder(
    get_response: Callable[[HttpRequest], HttpResponse],
) -> Callable[[HttpRequest], HttpResponse]:
    ...


@overload
def csp_excluder(
    get_response: Callable[[HttpRequest], Awaitable[HttpResponse]],
) -> Callable[[HttpRequest], Awaitable[HttpResponse]]:
    ...


def csp_excluder(
    get_response: Callable[[HttpRequest], HttpResponse]
    | Callable[[HttpRequest], Awaitable[HttpResponse]],
) -> (
    Callable[[HttpRequest], HttpResponse]
    | Callable[[HttpRequest], Awaitable[HttpResponse]]
):
    if iscoroutinefunction(get_response):

        async def async_middleware(request: HttpRequest) -> HttpResponse:
            response = await get_response(request)
            return _strip_csp_headers(request, response)

        return async_middleware

    def middleware(request: HttpRequest) -> HttpResponse:
        response = cast(HttpResponse, get_response(request))
        return _strip_csp_headers(request, response)

    return middleware


def _strip_csp_headers(
    request: HttpRequest,
    response: HttpResponse,
) -> HttpResponse:
    excluded_path_prefixes = tuple(
        getattr(settings, "CSP_EXCLUDE_PATH_PREFIXES", ("/admin",))
    )
    if request.path.startswith(excluded_path_prefixes):
        response.headers.pop("Content-Security-Policy", None)
        response.headers.pop("Content-Security-Policy-Report-Only", None)
    return response
