from typing import Any

from app.helpers.dict import remove_none_from_dict


def test_removes_none_correctly_for_root_with_empty_strings() -> None:
    initial: dict[str, Any] = {
        "a": 1,
        "b": None,
        "c": "",
        "d": {
            "e": "",
            "f": None,
        },
    }

    sut = remove_none_from_dict(
        initial=initial,
        nested=False,
        remove_empty_strings=False,
    )

    assert len(sut) == 3
    assert "b" not in sut
    assert "c" in sut

    nested = sut["d"]
    assert len(nested) == 2


def test_removes_none_correctly_for_nested_dict_with_empty_strings() -> None:
    initial: dict[str, dict[str, str | None] | None] = {
        "nested": {
            "a": "1",
            "b": None,
            "c": "",
        },
    }

    sut = remove_none_from_dict(
        initial=initial,
        nested=True,
        remove_empty_strings=False,
    )

    assert "nested" in sut
    assert len(sut["nested"]) == 2
    assert "b" not in sut["nested"]


def test_removes_none_and_empty_strings() -> None:
    initial: dict[str, Any] = {
        "a": 1,
        "b": "",
        "c": None,
        "nested": {
            "d": "1",
            "e": None,
            "f": "",
        },
    }

    sut = remove_none_from_dict(
        initial=initial,
        nested=True,
        remove_empty_strings=True,
    )

    assert "b" not in sut
    assert "c" not in sut
    assert len(sut) == 2

    nested = sut["nested"]
    assert len(nested) == 1
    assert "e" not in nested
    assert "f" not in nested
