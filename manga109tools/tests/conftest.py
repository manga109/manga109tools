from pathlib import Path
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--root_dir",
        type=Path,
    )
    parser.addoption(
        "--target_annot",
        type=str,
    )
    parser.addoption(
        "--exception_path",
        type=Path,
    )


@pytest.fixture(scope="session")
def root_dir(request: pytest.FixtureRequest) -> Path:
    return request.config.getoption("--root_dir")


@pytest.fixture(scope="session")
def target_annot(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--target_annot")
