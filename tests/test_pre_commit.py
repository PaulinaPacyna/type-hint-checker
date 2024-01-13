import os
import subprocess
from typing import Set

RUN_ALL_OUTPUT = {
    "",
    "INFO:annotation_checker:tests/cases/mixed_parameters.py: Missing annotation for "
    "parameter a "
    "(function f1), line 1",
    "INFO:annotation_checker:tests/cases/mixed_parameters.py: Missing return annotation "
    "for function f1, line 1",
    "INFO:annotation_checker:tests/cases/no_return.py: Missing return annotation "
    "for "
    "function f1, line 1",
    "INFO:annotation_checker:tests/cases/mixed_parameters_with_return.py: Missing "
    "annotation for "
    "parameter test_aa (function f5), line 1",
    "INFO:annotation_checker:tests/cases/comment_above.py: Missing annotation for "
    "parameter a (function f1), line 5",
    "INFO:annotation_checker:tests/cases/comment_above.py: Missing annotation for "
    "parameter b (function f1), line 5",
    "INFO:annotation_checker:tests/cases/comment_above.py: Missing return "
    "annotation for function f1, line 5",
    "INFO:annotation_checker:tests/cases/comment_below.py: Missing annotation for "
    "parameter a (function f1), line 4",
    "INFO:annotation_checker:tests/cases/comment_below.py: Missing annotation for "
    "parameter b (function f1), line 4",
    "INFO:annotation_checker:tests/cases/comment_below.py: Missing return "
    "annotation for function f1, line 4",
    "INFO:annotation_checker:tests/cases/different_comment.py: Missing annotation "
    "for parameter a (function f1), line 4",
    "INFO:annotation_checker:tests/cases/different_comment.py: Missing annotation "
    "for parameter b (function f1), line 4",
    "INFO:annotation_checker:tests/cases/different_comment.py: Missing return "
    "annotation for function f1, line 4",
    "INFO:annotation_checker:tests/cases/mixed_parameters_class.py: Missing annotation "
    "for parameter a (function f1), line 4",
    "INFO:annotation_checker:tests/cases/mixed_parameters_class.py: Missing return "
    "annotation for function f1, line 4",
    "INFO:annotation_checker:tests/cases/no_return_class.py: Missing return "
    "annotation for function f1, line 4",
    "INFO:annotation_checker:tests/cases/static_function_class.py: Missing "
    "annotation for parameter a (function f1), line 5",
}


def run_command(command: str) -> subprocess.CompletedProcess:
    """Common interface for executing command line programs"""
    return subprocess.run(
        command.split(), capture_output=True, universal_newlines=True, check=False
    )


def test_run_all() -> None:
    """Basic check"""
    process = run_command(
        "pre-commit run annotation_checker --all-files -c tests/configs/strict.yaml"
    )
    output = process.stdout
    lines = prepare_output(output)
    assert lines == {
        *RUN_ALL_OUTPUT,
        "annotation_checker......................................................."
        "Failed",
        "- hook id: annotation_checker",
        "- exit code: 1",
    }
    assert process.returncode == 1


def test_run_all_not_strict() -> None:
    """Test if pre-commit doesn't fail when strict=False"""
    process = run_command(
        "pre-commit run annotation_checker --all-files -c tests/configs/not-strict.yaml"
    )
    output = process.stdout
    lines = prepare_output(output)
    assert process.returncode == 0
    assert lines == {
        *RUN_ALL_OUTPUT,
        "annotation_checker......................................................."
        "Passed",
        "- hook id: annotation_checker",
    }


def prepare_output(output: str) -> Set[str]:
    """Prepares the output of the pylint program by splitting the lines, trimming and removing unnecessary output
    Parameters:
        output (str) - output of the command line program"""
    lines = output.split("\n")
    trimmed = [line.strip() for line in lines]
    result = [line for line in trimmed if "- duration: " not in line]

    return set(result)
