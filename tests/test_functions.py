import logging

import pathlib
import pytest
from pytest import fixture, raises

from annotation_checker.exceptions import IncorrectFileException
from annotation_checker.main import check_annotated, filter_files


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
    """Example of a function annotated with a string"""
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
    """Basic checks"""
    file = tmp_path / "file.py"
    file.write_text(request.getfixturevalue(input_), encoding="utf-8")
    assert check_annotated([file]) == result


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


def test_filepath_in_log(no_return, tmp_path: pathlib.Path, caplog) -> None:
    """Test if the path to th file appears in the log"""
    file = tmp_path / "file737ny73466364781.py"
    file.write_text(no_return, encoding="utf-8")
    with caplog.at_level(logging.INFO):
        check_annotated([file])
    assert "file737ny73466364781.py" in caplog.text


@pytest.mark.parametrize(
    "pattern,result",
    [
        ("^test", True),
        ("", False),
    ],
)
def test_exclude_parameters_by_regex(
    pattern, result, mixed_args_with_return, tmp_path: pathlib.Path
):
    """Test if parameters are excluded"""
    file = tmp_path / "file.py"
    file.write_text(mixed_args_with_return, encoding="utf-8")
    assert check_annotated([file], exclude_parameters=pattern) == result


@pytest.mark.parametrize(
    "input_,pattern,result",
    [
        ("mixed_args", "", False),
        ("no_return", "", False),
        ("mixed_args_with_return", "", False),
        ("mixed_args", "dgag", False),
        ("no_return", "adsg", False),
        ("mixed_args_with_return", "agddfa", False),
        ("mixed_args", "^f", True),
        ("no_return", "^f", True),
        ("mixed_args_with_return", "^f", True),
    ],
)
def test_exclude_by_name(input_, pattern, result, tmp_path: pathlib.Path, request):
    """Test excluding functions and classes by name"""
    file = tmp_path / "file.py"
    file.write_text(request.getfixturevalue(input_), encoding="utf-8")
    assert check_annotated([file], exclude_by_name=pattern) == result


def testing_multiple_files(
    mixed_args, no_return, mixed_args_with_return, tmp_path: pathlib.Path, caplog
):
    files_content_mapping = {
        "mixed_args.py": mixed_args,
        "no_return.py": no_return,
        "mixed_args_with_return.py": mixed_args_with_return,
    }
    files = []
    for case, content in files_content_mapping.items():
        file = tmp_path / case
        file.write_text(content, encoding="utf-8")
        files.append(file)
    with caplog.at_level(logging.INFO):
        check_annotated(list(files))
        assert all(filename in caplog.text for filename in files_content_mapping)
