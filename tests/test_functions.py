import logging

import pytest

from annotation_checker.exceptions import IncorrectFileException
from annotation_checker.main import check_annotated, filter_files
import pathlib
from pytest import fixture, raises


@fixture
def mixed_args_with_return() -> str:
    """Example of a function with a return type and some of the parameters are not
    annotated"""
    return "def f5(test_aa, bbb: int, ccc: 'Class') -> None:\n    pass"


@fixture
def mixed_args() -> str:
    """Example of a function without return type and some of the parameters are not
    annotated"""
    return "def f1(a, b: int):\n    return 5"


@fixture
def no_return() -> str:
    """Example of a function without a return type and annotated parameters"""
    return "def f1(a: int):\n    pass"


@fixture
def no_args() -> str:
    """Example of a function without arguments and with return type"""
    return "def f1() -> None:\n    pass"


@fixture
def not_a_function() -> str:
    """Should be omitted"""
    return "x=4"


@fixture
def incorrect_file() -> str:
    """Example of an incorrect file"""
    return "key1:\nkey2:"


@fixture
def string_annotation() -> str:
    return 'def f(self: "Class") -> int:\n    pass'


@pytest.mark.parametrize(
    "input_,result",
    [
        ("mixed_args", False),
        ("no_return", False),
        ("no_args", True),
        ("not_a_function", True),
        ("string_annotation", True),
        ("mixed_args_with_return", False),
    ],
)
def test_check_annotated(input_, result, tmp_path: pathlib.Path, request) -> None:
    file = tmp_path / "file.py"
    file.write_text(request.getfixturevalue(input_), encoding="utf-8")
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


def test_filter_files_no_exclude() -> None:
    file_list = ["file1.py", "file2.txt", "excluded/dir/file3.py", "", "test_file4.py"]
    result = ["file1.py", "excluded/dir/file3.py", "test_file4.py"]
    pattern = ""
    assert filter_files(file_list, pattern) == result


def test_filepath_in_log(no_return, tmp_path: pathlib.Path, caplog) -> None:
    file = tmp_path / "file737ny73466364781.py"
    file.write_text(no_return, encoding="utf-8")
    with caplog.at_level(logging.INFO):
        check_annotated([file])
    assert "file737ny73466364781.py" in caplog.text


def test_exclude_parameters_by_regex(mixed_args_with_return, tmp_path: pathlib.Path):
    file = tmp_path / "file.py"
    file.write_text(mixed_args_with_return, encoding="utf-8")
    assert check_annotated([file], exclude_parameters="^test")
