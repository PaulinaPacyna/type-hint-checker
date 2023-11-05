import subprocess

import pytest


def test_running_cli_version() -> None:
    subprocess.run(["annotation_checker", "no_return.py"])


def test_exclude_files() -> None:
    process = subprocess.run(
        [
            "annotation_checker",
            "--strict=True",
            r"--exclude_files=no_.*\.py",
            "no_args.py",
            "no_return.py",
            "not_a_function.py",
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert process.returncode == 0


@pytest.mark.parametrize(
    "filename,result",
    [
        ("mixed_args.py", 1),
        ("no_return.py", 1),
        ("no_args.py", 0),
        ("not_a_function.py", 0),
        ("mixed_args_with_return.py", 1),
    ],
)
def test_exit_code(filename: str, result: int) -> None:
    process = subprocess.run(
        ["annotation_checker", "--strict=True", filename],
        capture_output=True,
        universal_newlines=True,
    )
    assert result == process.returncode


def test_logging_filepath() -> None:
    process = subprocess.run(
        ["annotation_checker", "no_return.py"],
        capture_output=True,
        universal_newlines=True,
    )
    assert "no_return.py" in process.stderr


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
            "annotation_checker",
            "--strict=True",
            "mixed_args_with_return.py",
            f"--exclude_parameters={pattern}",
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert result == process.returncode


@pytest.mark.parametrize(
    "input_,pattern,result",
    [
        ("mixed_args.py", "", 1),
        ("no_return.py", "", 1),
        ("mixed_args_with_return.py", "", 1),
        ("mixed_args.py", "dgag", 1),
        ("no_return.py", "adsg", 1),
        ("mixed_args_with_return.py", "agddfa", 1),
        ("mixed_args.py", "^f", 0),
        ("no_return.py", "^f", 0),
        ("mixed_args_with_return.py", "^f", 0),
    ],
)
def test_exclude_by_name(input_: str, pattern: str, result: int) -> None:
    """Test excluding functions and classes by name"""
    process = subprocess.run(
        [
            "annotation_checker",
            "--strict=True",
            input_,
            f"--exclude_by_name={pattern}",
        ],
        capture_output=True,
        universal_newlines=True,
    )
    assert result == process.returncode


def test_debug_level():
    process = subprocess.run(
        ["annotation_checker", "no_return.py", "--log-level=DEBUG"],
        capture_output=True,
        universal_newlines=True,
    )
    assert "DEBUG:annotation_checker" in process.stderr
    assert "INFO:annotation_checker" in process.stderr
