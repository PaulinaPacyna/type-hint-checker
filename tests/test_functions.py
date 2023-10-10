import pytest

from annotation_checker.exceptions import IncorrectFileException
from annotation_checker.main import check_annotated
import pathlib
from pytest import fixture, raises


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


@fixture
def incorrect_file():
    return "key1:\nkey2:"


@fixture
def string_annotation():
    return 'def f(self: "Class") -> int:\n    pass'


@pytest.mark.parametrize(
    "input,result",
    [
        ("mixed_args", False),
        ("no_return", False),
        ("no_args", True),
        ("not_a_function", True),
        ("string_annotation", True),
    ],
)
def test_check_annotated(input, result, tmp_path: pathlib.Path, request):
    file = tmp_path / "file.py"
    file.write_text(request.getfixturevalue(input), encoding="utf-8")
    assert check_annotated([file]) == result


def test_incorrect_file(incorrect_file, tmp_path: pathlib.Path):
    file = tmp_path / "file737ny73814781.py"
    file.write_text(incorrect_file, encoding="utf-8")
    with raises(IncorrectFileException) as exception:
        check_annotated([file])
    assert "file737ny73814781.py" in str(exception)
