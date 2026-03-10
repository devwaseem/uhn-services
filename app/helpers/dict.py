from typing import Any, Mapping, TypeVar, cast

K = TypeVar("K")
V = TypeVar("V")


def remove_none_from_dict(
    initial: Mapping[K, V | None],
    *,
    nested: bool = True,
    remove_empty_strings: bool = False,
) -> dict[K, V]:
    new_dict: dict[K, V] = {}

    for key, value in initial.items():
        if value is None:
            continue

        if nested and isinstance(value, Mapping):
            cleaned = remove_none_from_dict(
                cast(Mapping[Any, Any | None], value),
                nested=nested,
                remove_empty_strings=remove_empty_strings,
            )
            new_dict[key] = cast(V, cleaned)

        elif isinstance(value, str):
            if remove_empty_strings and value == "":
                continue
            new_dict[key] = value

        else:
            new_dict[key] = value

    return new_dict
