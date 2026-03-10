from typing import Any

from frontend.layouts.base import BaseLayout


class PasswordResetFromKeyPage(BaseLayout):
    def __init__(self, context: dict[str, Any]) -> None:
        super().__init__(title="Set New Password")
        self._context = context

    def get_context(self) -> dict[str, Any]:
        self._context["page"] = self
        return self._context
