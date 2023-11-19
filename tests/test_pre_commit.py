import os
import subprocess


def run_command(command: str) -> subprocess.CompletedProcess:
    shell_path = os.getenv("ANNOTATION_CHECKER_SHELL_PATH")
    if shell_path:
        command = f'{shell_path}, -c "{command}"'
    return subprocess.run(
        command,
        capture_output=True,
        universal_newlines=True,
        shell=False,
    )


def test_run_all() -> None:
    process = run_command(
        "pre-commit run annotation_checker --all-files -c tests/configs/strict.yaml"
    )
    lines = process.stdout.split("\n")
    lines = [line.strip() for line in lines]
    assert set(lines) == {
        "",
        "annotation_checker.......................................................Failed",
        "- hook id: annotation_checker",
        "- exit code: 1",
        "INFO:annotation_checker:tests/cases/mixed_args.py: Missing annotation for argument a "
        "(function f1), line 1",
        "INFO:annotation_checker:tests/cases/mixed_args.py: Missing return annotation "
        "for function f1, line 1",
        "INFO:annotation_checker:tests/cases/no_return.py: Missing return annotation for "
        "function f1, line 1",
        "INFO:annotation_checker:tests/cases/mixed_args_with_return.py: Missing annotation for "
        "argument test_aa (function f5), line 1",
    }
    assert process.returncode == 1


def test_run_all_not_strict() -> None:
    process = run_command(
        "pre-commit run annotation_checker --all-files -c tests/configs/not-strict.yaml"
    )
    print(process.args)
    lines = process.stdout.split("\n") + process.stderr.split("\n")
    lines = [line.strip() for line in lines]
    print(lines)
    assert process.returncode == 0
