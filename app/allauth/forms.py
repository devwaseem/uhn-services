from allauth.account.forms import ResetPasswordForm as BaseResetPasswordForm
from allauth.account.forms import SignupForm as BaseSignupForm
from django.http.request import HttpRequest


class ResetPasswordForm(BaseResetPasswordForm):  # type: ignore
    def _send_unknown_account_mail(
        self, request: HttpRequest, email: str
    ) -> None:
        # Overriding this method to prevent sending emails to unknown accounts
        pass


class SignupForm(BaseSignupForm):  # type: ignore
    def _send_account_already_exists_mail(self, request: HttpRequest) -> None:
        # Overriding this method to prevent sending emails
        # to account already exists accounts
        pass
