import logging

import pathlib
import pytest
from pytest import fixture, raises

from type_hint_checker.exceptions import IncorrectFileException
from type_hint_checker.main import check_type_hints, filter_files


NO_RETURN = "tests/cases/no_return.py"
MIXED_ARGS = "tests/cases/mixed_parameters.py"
NO_ARGS = "tests/cases/no_parameters.py"
NOT_A_FUNCTION = "tests/cases/not_a_function.py"
STRING_TYPE_HINT = "tests/cases/string_type_hint.py"
MIXED_ARGS_WITH_RETURN = "tests/cases/mixed_parameters_with_return.py"
COMMENT_ABOVE = "tests/cases/comment_above.py"
COMMENT_BELOW = "tests/cases/comment_below.py"
COMMENT_BODY = "tests/cases/comment_body.py"
MANY_COMMENTS = "tests/cases/many_comments.py"
DIFFERENT_COMMENT = "tests/cases/different_comment.py"
COMMENT_HEADER = "tests/cases/comment_header.py"
COMMENT_LONG_HEADER = "tests/cases/comment_long_header.py"
COMMENT_LONG_HEADER_2 = "tests/cases/comment_long_header_2.py"
EMPTY_CLASS = "tests/cases/empty_class.py"
MIXED_ARGS_CLASS = "tests/cases/mixed_parameters_class.py"
NO_RETURN_CLASS = "tests/cases/no_return_class.py"
PROPERLY_ANNOTATED_CLASS = "tests/cases/properly_annotated_class.py"
STATIC_FUNCTION_CLASS = "tests/cases/static_function_class.py"
ANNOTATED_SELF_CLASS = "tests/cases/annotated_self_class.py"


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
        (STRING_TYPE_HINT, True),
        (MIXED_ARGS_WITH_RETURN, False),
        (COMMENT_ABOVE, False),
        (COMMENT_BELOW, False),
        (COMMENT_BODY, True),
        (MANY_COMMENTS, True),
        (COMMENT_HEADER, True),
        (COMMENT_LONG_HEADER, True),
        (COMMENT_LONG_HEADER_2, True),
    ],
)
def test_check_type_hints(input_path: str, result: bool) -> None:
    assert check_type_hints([input_path]) == result


@pytest.mark.parametrize(
    "input_path,ignore_comment,result",
    [
        (COMMENT_BODY, "jdncajbc", False),
        (COMMENT_BODY, "custom", False),
        (DIFFERENT_COMMENT, "custom", True),
    ],
)
def test_custom_ignore_comment(
    input_path: str, ignore_comment: str, result: bool
) -> None:
    assert check_type_hints([input_path], ignore_comment=ignore_comment) == result


def test_incorrect_file(incorrect_file, tmp_path: pathlib.Path) -> None:
    """Test if passing incorrect file raises the correct error"""
    file = tmp_path / "file737ny73814781.py"
    file.write_text(incorrect_file, encoding="utf-8")
    with raises(IncorrectFileException) as exception:
        check_type_hints([file])
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
        check_type_hints([NO_RETURN])
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
        check_type_hints([MIXED_ARGS_WITH_RETURN], exclude_parameters=pattern) == result
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
    assert check_type_hints([input_file], exclude_by_name=pattern) == result


def testing_multiple_files(caplog):
    file_list = [MIXED_ARGS, NO_RETURN, MIXED_ARGS_WITH_RETURN]
    with caplog.at_level(logging.INFO):
        check_type_hints(file_list)
        assert all(filename in caplog.text for filename in file_list)


@pytest.mark.parametrize(
    "input_path,result",
    [
        (EMPTY_CLASS, True),
        (MIXED_ARGS_CLASS, False),
        (NO_RETURN_CLASS, False),
        (PROPERLY_ANNOTATED_CLASS, True),
        (STATIC_FUNCTION_CLASS, False),
    ],
)
def test_in_a_class(input_path, result) -> None:
    assert check_type_hints([input_path]) == result


def test_exclude_self() -> None:
    assert check_type_hints([STATIC_FUNCTION_CLASS], exclude_parameters="") == False
    assert check_type_hints([PROPERLY_ANNOTATED_CLASS], exclude_parameters="") == False
    assert check_type_hints([PROPERLY_ANNOTATED_CLASS]) == True
    assert check_type_hints([ANNOTATED_SELF_CLASS], exclude_parameters="") == True
