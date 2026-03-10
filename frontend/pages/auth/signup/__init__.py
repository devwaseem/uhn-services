from typing import Any

from frontend.layouts.base import BaseLayout


class SignupPage(BaseLayout):
    def __init__(self, context: dict[str, Any]) -> None:
        super().__init__(title="Create Account")
        self._context = context

    def get_context(self) -> dict[str, Any]:
        self._context["page"] = self
        return self._context
