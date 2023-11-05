import logging
import os

import pathlib
import pytest
from pytest import fixture, raises

from annotation_checker.exceptions import IncorrectFileException
from annotation_checker.main import check_annotated, filter_files


NO_RETURN = "tests/cases/no_return.py"
MIXED_ARGS = "tests/cases/mixed_args.py"
NO_ARGS = "tests/cases/no_args.py"
NOT_A_FUNCTION = "tests/cases/not_a_function.py"
STRING_ANNOTATION = "tests/cases/string_annotation.py"
MIXED_ARGS_WITH_RETURN = "tests/cases/mixed_args_with_return.py"


@fixture
def incorrect_file() -> str:
    """Example of an incorrect file"""
    return "key1:\nkey2:"


@pytest.mark.parametrize(
    "input_path,result",
    [
        (MIXED_ARGS, False),
        (NO_RETURN, False),
        (NO_ARGS, True),
        (NOT_A_FUNCTION, True),
        (STRING_ANNOTATION, True),
        (MIXED_ARGS_WITH_RETURN, False),
    ],
)
def test_check_annotated(input_path, result) -> None:
    assert check_annotated([input_path]) == result


def test_incorrect_file(incorrect_file, tmp_path: pathlib.Path) -> None:
    """Test if passing incorrect file raises the correct error"""
    file = tmp_path / "file737ny73814781.py"
    file.write_text(incorrect_file, encoding="utf-8")
    with raises(IncorrectFileException) as exception:
        check_annotated([file])
    assert "file737ny73814781.py" in str(exception)


def test_filter_files() -> None:
    """Test filtering files by regex"""
    file_list = ["file1.py", "file2.txt", "excluded/dir/file3.py", "", "test_file4.py"]
    result = ["file1.py"]
    pattern = r"(excluded/|test_)"
    assert filter_files(file_list, pattern) == result


def test_filter_files_no_exclude() -> None:
    """Test default file filter"""
    file_list = ["file1.py", "file2.txt", "excluded/dir/file3.py", "", "test_file4.py"]
    result = ["file1.py", "excluded/dir/file3.py", "test_file4.py"]
    pattern = ""
    assert filter_files(file_list, pattern) == result


def test_filepath_in_log(caplog) -> None:
    """Test if the path to th file appears in the log"""
    with caplog.at_level(logging.INFO):
        check_annotated([NO_RETURN])
    assert NO_RETURN in caplog.text


@pytest.mark.parametrize(
    "pattern,result",
    [
        ("^test", True),
        ("", False),
    ],
)
def test_exclude_parameters_by_regex(pattern, result):
    """Test if parameters are excluded"""
    assert (
        check_annotated([MIXED_ARGS_WITH_RETURN], exclude_parameters=pattern) == result
    )


@pytest.mark.parametrize(
    "input_file,pattern,result",
    [
        (MIXED_ARGS, "", False),
        (NO_RETURN, "", False),
        (MIXED_ARGS_WITH_RETURN, "", False),
        (MIXED_ARGS, "dgag", False),
        (NO_RETURN, "adsg", False),
        (MIXED_ARGS_WITH_RETURN, "agddfa", False),
        (MIXED_ARGS, "^f", True),
        (NO_RETURN, "^f", True),
        (MIXED_ARGS_WITH_RETURN, "^f", True),
    ],
)
def test_exclude_by_name(input_file, pattern, result):
    """Test excluding functions and classes by name"""
    assert check_annotated([input_file], exclude_by_name=pattern) == result


def testing_multiple_files(caplog):
    file_list = [MIXED_ARGS, NO_RETURN, MIXED_ARGS_WITH_RETURN]
    with caplog.at_level(logging.INFO):
        check_annotated(file_list)
        assert all(filename in caplog.text for filename in file_list)
