from django.http import HttpRequest

from app.account.models import User


class HTTPAuthRequest(HttpRequest):
    user: User
