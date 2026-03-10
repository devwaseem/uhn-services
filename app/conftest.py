from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Generator

import pytest


@pytest.fixture(autouse=True)
def _set_tmp_media_storage(settings: Any) -> Generator[None, Any, None]:
    with TemporaryDirectory(prefix="test") as tmpdir:
        settings.STORAGES["default"]["OPTIONS"]["location"] = tmpdir
        yield


@pytest.fixture()
def data_path() -> Path:
    return Path(__file__).parent / "data"
