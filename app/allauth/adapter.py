from collections.abc import Callable
from typing import Any, Literal, cast

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.core.mail import EmailMessage
from django.http import HttpRequest

from app.context_processors import get_site_data


class AllAuthAccountAdapter(DefaultAccountAdapter):
    request: HttpRequest

    def is_open_for_signup(
        self,
        request: HttpRequest,
    ) -> Literal[True]:
        del request
        allow_registration = bool(
            getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)
        )
        return cast(Literal[True], allow_registration)

    def send_mail(
        self,
        template_prefix: str,
        email: str,
        context: dict[str, Any],
    ) -> None:
        context.update(get_site_data(request=self.request))
        typed_render_mail = cast(
            Callable[[str, str, dict[str, Any]], EmailMessage],
            self.render_mail,
        )
        msg = typed_render_mail(template_prefix, email, context)
        msg.send()

    def format_email_subject(self, subject: str) -> str:
        site_data = get_site_data(request=self.request)
        prefix = site_data["site_name"]
        if prefix is None:
            return subject
        return f"{prefix}: {subject}"
