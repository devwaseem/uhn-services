from uuid import uuid4

import pytest
from mixer.backend.django import mixer

from app.account.models import User
from app.helpers import django_models


@pytest.mark.django_db
def test_returns_none_if_object_does_not_exist() -> None:
    user_id = uuid4()
    User.objects.filter(
        id=user_id
    ).delete()  # making sure user with this id does not exist

    sut = django_models.get_object_or_none(User, id=user_id)

    assert sut is None


@pytest.mark.django_db
def test_returns_object_if_object_exist() -> None:
    user_id = uuid4()
    mixer.blend(User, id=user_id)  # create user with this id

    sut = django_models.get_object_or_none(User, id=user_id)

    assert sut is not None
