from typing import TypedDict

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest



class DomainContext(TypedDict):
    domain_name: str
    site_name: str | None
    protocol: str
    base_url: str
    static_url: str
    media_url: str


def get_site_data(request: HttpRequest) -> DomainContext:
    site = get_current_site(request)
    site_name = site.name
    domain_name = site.domain
    protocol = "https" if request.is_secure() else "http"
    base_url = f"{protocol}://{domain_name}"

    return DomainContext(
        domain_name=domain_name,
        site_name=site_name,
        protocol=protocol,
        base_url=base_url,
        static_url=settings.STATIC_URL,
        media_url=settings.MEDIA_URL,
    )


class AllAuthSetting(TypedDict):
    ACCOUNT_ALLOW_REGISTRATION: bool


def allauth_settings(_request: HttpRequest) -> AllAuthSetting:
    """Expose some settings from django-allauth in templates."""
    return {
        "ACCOUNT_ALLOW_REGISTRATION": getattr(
            settings, "ACCOUNT_ALLOW_REGISTRATION", True
        )
    }
