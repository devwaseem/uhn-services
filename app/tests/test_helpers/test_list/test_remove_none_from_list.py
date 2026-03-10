from app.helpers.list import remove_none_from_list


def test_removes_none_elements_correctly() -> None:
    initial = ["a", "b", None]

    sut = remove_none_from_list(initial_list=initial)

    assert len(sut) == 2
    assert sut == ["a", "b"]
