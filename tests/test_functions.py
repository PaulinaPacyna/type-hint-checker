import pytest

from annotation_checker.main import check_annotated
import pathlib
from pytest import fixture


@fixture
def mixed_args():
    return "def f1(a, b: int):\n    return 5"


@fixture
def no_return():
    return "def f1(a: int):\n    pass"


@fixture
def no_args():
    return "def f1() -> None:\n    pass"


@fixture
def not_a_function():
    return "x=4"


@pytest.mark.parametrize(
    "input,result",
    [
        ("mixed_args", False),
        ("no_return", False),
        ("no_args", True),
        ("not_a_function", True),
    ],
)
def test_check_annotated(input, result, tmp_path: pathlib.Path, request):
    file = tmp_path / "file.py"
    file.write_text(request.getfixturevalue(input), encoding="utf-8")
    assert check_annotated([file]) == result
