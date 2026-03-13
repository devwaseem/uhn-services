from typing import Any

from django import forms
from django.contrib import admin
from django.http import HttpRequest

from app.api_auth.models import APIKey, APIScopes


class APIKeyAdminNewForm(forms.ModelForm[APIKey]):
    class Meta:
        model = APIKey
        fields = (
            "name",
            "description",
        )
        widgets = {
            "expires_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
            ),
        }

    def save(self, commit: bool = True) -> APIKey:  # noqa
        self.instance.generate_key(commit=False)
        return super().save(commit=commit)


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin[APIKey]):
    list_display = (
        "name",
        "is_active",
        "key_prefix",
        "expires_at",
        "last_used_at",
        "created_at",
    )
    readonly_fields = (
        "decrypted_key",
        "key_prefix",
        "key_hash",
        "created_at",
        "last_used_at",
        "last_used_ip",
    )
    filter_horizontal = ("allowed_solutions",)
    list_filter = ("is_active",)

    fieldsets = (
        (
            "Security",
            {
                "fields": (
                    "decrypted_key",
                    "key_prefix",
                    "key_hash",
                    "is_active",
                    "expires_at",
                    "revoked_at",
                )
            },
        ),
        (
            "Details",
            {
                "fields": (
                    "name",
                    "description",
                    "allowed_solutions",
                    "created_at",
                    "last_used_at",
                    "last_used_ip",
                )
            },
        ),
    )

    @admin.display(description="API key")
    def decrypted_key(self, obj: APIKey) -> str:
        return obj.get_raw_key()

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

    def get_fieldsets(
        self,
        request: HttpRequest,
        obj: APIKey | None = None,
    ) -> Any:
        _ = request
        if obj is None:
            return (
                (
                    "Details",
                    {
                        "fields": (
                            "name",
                            "description",
                        )
                    },
                ),
            )
        return self.fieldsets


@admin.register(APIScopes)
class APIScopeAdmin(admin.ModelAdmin[APIScopes]):
    list_display = ("slug", "is_active", "description")
    list_filter = ("is_active",)

    def get_readonly_fields(
        self,
        request: HttpRequest,
        obj: APIScopes | None = None,
    ) -> tuple[str, ...]:
        _ = request
        if obj is None:
            return ()
        return ("slug",)
