from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponse
from .request import HTTPAuthRequest

class SuperUserLoginRequiredMixin(AccessMixin):
    def dispatch(
        self,
        request: HTTPAuthRequest,
        *args: str,
        **kwargs: str,
    ) -> HttpResponse:
        if request.user.is_authenticated and request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)  # type: ignore

        return self.handle_no_permission()
