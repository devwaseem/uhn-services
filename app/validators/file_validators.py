from __future__ import annotations

from typing import Any

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileSizeValidatorInMb:
    message = _(
        "The file size is %(current_file_size)s MB, "
        "exceeding the maximum file size of %(max_file_size)s MB "
    )
    code = "file_size_exceeded"

    def __init__(
        self,
        max_size_in_mb: int,
        message: str | None = None,
        code: str | None = None,
    ) -> None:
        self.max_size_in_mb = max_size_in_mb
        if message is not None:
            self.message = _(message)
        if code is not None:
            self.code = code

    def __call__(self, value: Any) -> None:
        current_file_size = (value.size / 1024) / 1024
        max_file_size = self.max_size_in_mb * 1024 * 1024
        if value.size > max_file_size:
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "current_file_size": str(round(current_file_size, 2)),
                    "max_file_size": str(self.max_size_in_mb),
                },
            )

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, self.__class__)
            and self.max_size_in_mb == other.max_size_in_mb
            and self.message == other.message
            and self.code == other.code
        )
