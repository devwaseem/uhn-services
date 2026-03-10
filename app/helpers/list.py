from typing import TypeVar

T = TypeVar("T")
V = TypeVar("V")


def remove_none_from_list(
    initial_list: list[T | None],
) -> list[T]:
    return [i for i in initial_list if i is not None]
