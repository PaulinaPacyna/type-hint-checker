import pytest

from annotation_checker.exceptions import IncorrectFileException
from annotation_checker.main import check_annotated, filter_files
import pathlib
from pytest import fixture, raises


@fixture
def mixed_args() -> str:
    return "def f1(a, b: int):\n    return 5"


@fixture
def no_return() -> str:
    return "def f1(a: int):\n    pass"


@fixture
def no_args() -> str:
    return "def f1() -> None:\n    pass"


@fixture
def not_a_function() -> str:
    return "x=4"


@fixture
def incorrect_file() -> str:
    return "key1:\nkey2:"


@fixture
def string_annotation() -> str:
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
def test_check_annotated(input, result, tmp_path: pathlib.Path, request) -> None:
    file = tmp_path / "file.py"
    file.write_text(request.getfixturevalue(input), encoding="utf-8")
    assert check_annotated([file]) == result


def test_incorrect_file(incorrect_file, tmp_path: pathlib.Path) -> None:
    file = tmp_path / "file737ny73814781.py"
    file.write_text(incorrect_file, encoding="utf-8")
    with raises(IncorrectFileException) as exception:
        check_annotated([file])
    assert "file737ny73814781.py" in str(exception)


def test_filter_files() -> None:
    file_list = ["file1.py", "file2.txt", "excluded/dir/file3.py", "", "test_file4.py"]
    result = ["file1.py"]
    pattern = r"(excluded/|test_)"
    assert filter_files(file_list, pattern) == result
