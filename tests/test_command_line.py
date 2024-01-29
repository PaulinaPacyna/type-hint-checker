import subprocess

import pytest

NO_RETURN = "tests/cases/no_return.py"
MIXED_ARGS = "tests/cases/mixed_parameters.py"
NO_ARGS = "tests/cases/no_parameters.py"
NOT_A_FUNCTION = "tests/cases/not_a_function.py"
MIXED_ARGS_WITH_RETURN = "tests/cases/mixed_parameters_with_return.py"
DIFFERENT_COMMENT = "tests/cases/different_comment.py"


def test_running_cli_version() -> None:
    subprocess.run(["type_hint_checker", NO_RETURN])


def test_exclude_files() -> None:
    process = subprocess.run(
        [
            "type_hint_checker",
            r"--exclude_files=no_.*\.py",
            NO_ARGS,
            NO_RETURN,
            NOT_A_FUNCTION,
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 0


@pytest.mark.parametrize(
    "filename,result",
    [
        (MIXED_ARGS, 1),
        (NO_RETURN, 1),
        (NO_ARGS, 0),
        (NOT_A_FUNCTION, 0),
        (MIXED_ARGS_WITH_RETURN, 1),
    ],
)
def test_exit_code(filename: str, result: int) -> None:
    process = subprocess.run(
        ["type_hint_checker", filename],
        capture_output=True,
        universal_newlines=True,
    )
    assert result == process.returncode


@pytest.mark.parametrize(
    "filename",
    [
        MIXED_ARGS,
        NO_RETURN,
        MIXED_ARGS_WITH_RETURN,
    ],
)
def test_exit_code_with_exit_zero(filename: str) -> None:
    process = subprocess.run(
        ["type_hint_checker", filename, "--exit_zero"],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 0


def test_logging_filepath() -> None:
    process = subprocess.run(
        ["type_hint_checker", NO_RETURN],
        capture_output=True,
        universal_newlines=True,
    )
    assert NO_RETURN in process.stderr


@pytest.mark.parametrize(
    "pattern,result",
    [
        ("^test", 0),
        ("", 1),
    ],
)
def test_exclude_parameters(pattern: str, result: int) -> None:
    process = subprocess.run(
        [
            "type_hint_checker",
            MIXED_ARGS_WITH_RETURN,
            f"--exclude_parameters={pattern}",
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert result == process.returncode


@pytest.mark.parametrize(
    "input_,pattern,result",
    [
        (MIXED_ARGS, "", 1),
        (NO_RETURN, "", 1),
        (MIXED_ARGS_WITH_RETURN, "", 1),
        (MIXED_ARGS, "dgag", 1),
        (NO_RETURN, "adsg", 1),
        (MIXED_ARGS_WITH_RETURN, "agddfa", 1),
        (MIXED_ARGS, "^f", 0),
        (NO_RETURN, "^f", 0),
        (MIXED_ARGS_WITH_RETURN, "^f", 0),
    ],
)
def test_exclude_by_name(input_: str, pattern: str, result: int) -> None:
    """Test excluding functions and classes by name"""
    process = subprocess.run(
        [
            "type_hint_checker",
            input_,
            f"--exclude_by_name={pattern}",
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert result == process.returncode


def test_debug_level():
    process = subprocess.run(
        ["type_hint_checker", NO_RETURN, "--log-level=DEBUG"],
        capture_output=True,
        universal_newlines=True,
    )
    assert "DEBUG:type_hint_checker" in process.stderr
    assert "INFO:type_hint_checker" in process.stderr


def test_ignore_comment():
    process = subprocess.run(
        [
            "type_hint_checker",
            DIFFERENT_COMMENT,
            "--ignore_comment=custom",
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 0
    process = subprocess.run(
        [
            "type_hint_checker",
            DIFFERENT_COMMENT,
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 1
