from typing import Any

from django.contrib import admin
from django.forms import ModelForm
from ipware.ip import HttpRequest

from app.api_auth.models import APIKey, APISolution


class APIKeyAdminNewForm(ModelForm[APIKey]):
    class Meta:
        model = APIKey
        fields = ("name", "description")

    def save(self, commit: bool = True) -> APIKey:  # noqa
        self.instance.generate_key(commit=False)
        return super().save(commit=commit)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin[APIKey]):
    list_display = ("name",)
    readonly_fields = ("key",)
    filter_horizontal = ("allowed_solutions",)

    fieldsets = (
        (
            "Security",
            {"fields": ("key", "is_active")},
        ),
        ("Details", {"fields": ("name", "description", "allowed_solutions")}),
    )

    def get_form(
        self,
        request: HttpRequest,
        obj: APIKey | None = None,
        change: bool = False,  # noqa
        **kwargs: Any,
    ) -> Any:
        if obj is None:
            return APIKeyAdminNewForm
        return super().get_form(request, obj, **kwargs)


@admin.register(APISolution)
class APISolutionAdmin(admin.ModelAdmin[APISolution]):
    list_display = ("name", "description")
