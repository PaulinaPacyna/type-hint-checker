import os
import subprocess
from typing import Set

RUN_ALL_OUTPUT = {
    "",
    "INFO:type_hint_checker:tests/cases/mixed_parameters.py: Missing type hint for "
    "parameter a "
    "(function f1), line 1",
    "INFO:type_hint_checker:tests/cases/mixed_parameters.py: Missing return type hint "
    "for function f1, line 1",
    "INFO:type_hint_checker:tests/cases/no_return.py: Missing return type hint "
    "for "
    "function f1, line 1",
    "INFO:type_hint_checker:tests/cases/mixed_parameters_with_return.py: Missing "
    "type hint for "
    "parameter test_aa (function f5), line 1",
    "INFO:type_hint_checker:tests/cases/comment_above.py: Missing type hint for "
    "parameter a (function f1), line 5",
    "INFO:type_hint_checker:tests/cases/comment_above.py: Missing type hint for "
    "parameter b (function f1), line 5",
    "INFO:type_hint_checker:tests/cases/comment_above.py: Missing return "
    "type hint for function f1, line 5",
    "INFO:type_hint_checker:tests/cases/comment_below.py: Missing type hint for "
    "parameter a (function f1), line 4",
    "INFO:type_hint_checker:tests/cases/comment_below.py: Missing type hint for "
    "parameter b (function f1), line 4",
    "INFO:type_hint_checker:tests/cases/comment_below.py: Missing return "
    "type hint for function f1, line 4",
    "INFO:type_hint_checker:tests/cases/different_comment.py: Missing type hint "
    "for parameter a (function f1), line 4",
    "INFO:type_hint_checker:tests/cases/different_comment.py: Missing type hint "
    "for parameter b (function f1), line 4",
    "INFO:type_hint_checker:tests/cases/different_comment.py: Missing return "
    "type hint for function f1, line 4",
    "INFO:type_hint_checker:tests/cases/mixed_parameters_class.py: Missing type hint "
    "for parameter a (function f1), line 4",
    "INFO:type_hint_checker:tests/cases/mixed_parameters_class.py: Missing return "
    "type hint for function f1, line 4",
    "INFO:type_hint_checker:tests/cases/no_return_class.py: Missing return "
    "type hint for function f1, line 4",
    "INFO:type_hint_checker:tests/cases/static_function_class.py: Missing "
    "type hint for parameter a (function f1), line 5",
}


def run_command(command: str) -> subprocess.CompletedProcess:
    """Common interface for executing command line programs"""
    return subprocess.run(
        command.split(), capture_output=True, universal_newlines=True, check=False
    )


def test_run_all() -> None:
    """Basic check"""
    process = run_command(
        "pre-commit run type_hint_checker --all-files -c tests/configs/strict.yaml"
    )
    output = process.stdout
    lines = prepare_output(output)
    assert lines == {
        *RUN_ALL_OUTPUT,
        "type_hint_checker........................................................"
        "Failed",
        "- hook id: type_hint_checker",
        "- exit code: 1",
    }
    assert process.returncode == 1


def test_run_all_not_strict() -> None:
    """Test if pre-commit doesn't fail when strict=False"""
    process = run_command(
        "pre-commit run type_hint_checker --all-files -c tests/configs/not-strict.yaml"
    )
    output = process.stdout
    lines = prepare_output(output)
    assert lines == {
        *RUN_ALL_OUTPUT,
        "type_hint_checker........................................................"
        "Passed",
        "- hook id: type_hint_checker",
    }
    assert process.returncode == 0


def prepare_output(output: str) -> Set[str]:
    """Prepares the output of the pylint program by splitting the lines, trimming and
    removing unnecessary output
    Parameters:
        output (str) - output of the command line program"""
    lines = output.split("\n")
    trimmed = [line.strip() for line in lines]
    result = []
    not_needed_phrases = [
        "- duration: ",
        "Once installed this environment will be reused.",
        "This may take a few minutes...",
        "Installing environment for ",
        "Initializing environment for",
    ]
    for line in trimmed:
        if not any([phrase in line for phrase in not_needed_phrases]):
            result += [line]
    return set(result)
