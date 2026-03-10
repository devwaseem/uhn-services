from typing import Any, Type, TypeVar

from django.db.models import Model

T = TypeVar("T", bound=Model)


def get_object_or_none(model_class: Type[T], **kwargs: object) -> T | None:
    try:
        return model_class.objects.get(**kwargs)  # type: ignore
    except model_class.DoesNotExist:  # type: ignore
        return None


def update_model_field_if_empty(
    *,
    instance: Model,
    attr: str,
    value: Any,
) -> None:
    if not hasattr(instance, attr):
        raise KeyError(f"{attr} not found in {type(instance)}")

    field_value = getattr(instance, attr)
    if field_value is None or field_value == "":
        setattr(instance, attr, value)


def update_model_field(
    *,
    instance: Model,
    attr: str,
    value: Any,
    cast: Type[Any] | None = None,
) -> None:
    if not hasattr(instance, attr):
        raise TypeError(f"{attr} not found in {type(instance)}")

    if cast:
        setattr(instance, attr, cast(value))
    else:
        setattr(instance, attr, value)
