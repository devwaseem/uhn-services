from typing import Any

from django.http import HttpRequest, HttpResponse
from django.template import loader


def render_multiple_templates(
    *,
    request: HttpRequest,
    template_name_list: tuple[str, ...] | list[str],
    context: dict[str, Any] | None = None,
    content_type: str | None = None,
    status: int | None = None,
    using: str | None = None,
) -> HttpResponse:
    content = "\n".join(
        [
            loader.render_to_string(
                template_name=template_name,
                context=context,
                request=request,
                using=using,
            )
            for template_name in template_name_list
        ]
    )

    return HttpResponse(
        content=content,
        content_type=content_type,
        status=status,
    )
