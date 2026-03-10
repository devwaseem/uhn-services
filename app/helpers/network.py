from django.http import HttpRequest
from ipware import get_client_ip


def get_ip_from_request(request: HttpRequest) -> str | None:
    ip_address, is_routable = get_client_ip(request)
    if ip_address is not None and is_routable:
        return str(ip_address)
    return None
