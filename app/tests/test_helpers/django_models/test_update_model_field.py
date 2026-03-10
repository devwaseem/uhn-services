from typing import cast

import faker
import pytest
from mixer.backend.django import mixer

from app.account.models import User
from app.helpers import django_models

fake = faker.Faker()


@pytest.mark.django_db
def test_throws_type_error_if_field_does_not_exist() -> None:
    expected_name = fake.name()
    user = cast(User, mixer.blend(User, name="SOMETHING"))

    with pytest.raises(
        TypeError, match=f"__non_existent_field__ not found in {type(user)}"
    ):
        django_models.update_model_field(
            instance=user,
            attr="__non_existent_field__",
            value=expected_name,
        )


@pytest.mark.django_db
def test_updates_field_correctly_if_field_exists() -> None:
    expected_name = fake.name()
    user = cast(User, mixer.blend(User, name="SOMETHING"))

    django_models.update_model_field(
        instance=user,
        attr="name",
        value=expected_name,
    )

    assert user.name == expected_name


@pytest.mark.django_db
def test_updates_field_correctly_with_cast_if_field_exists() -> None:
    user = cast(User, mixer.blend(User, name="SOMETHING"))

    django_models.update_model_field(
        instance=user,
        attr="name",
        value=12345,
        cast=str,
    )

    assert user.name == "12345"
