import argparse
import re
import sys
from typing import List
import logging
import ast

from annotation_checker.checkers import FunctionChecker, ClassChecker
from annotation_checker.exceptions import IncorrectFileException

logger = logging.getLogger("annotation_checker")
logging.basicConfig()


def check_annotated(
    file_list: List[str], exclude_parameters: str = "", exclude_self: bool = False
) -> bool:
    """
    Iterates through the list of file paths, parses the files and checks if all
    functions and classes in the files are type-annotated.
    Parameters
    ----------
        file_list: List[str] - Filenames to be checked by
        exclude_parameters: str - regex specifying which parameters should not be
                            checked
        exclude_self: bool - if True, omit type checking for the first parameter in
                            methods
    Returns
    ----------
        True if all files are type-annotated.
    """
    result = True
    for filename in file_list:
        with open(filename, "r", encoding="utf-8") as file:
            content = file.read()
            try:
                body = ast.parse(content).body
            except SyntaxError as exc:
                raise IncorrectFileException(
                    f"File could not be parsed: {filename}"
                ) from exc
            for item in body:
                if isinstance(item, ast.FunctionDef):
                    checker = FunctionChecker(exclude_parameters=exclude_parameters)
                elif isinstance(item, ast.ClassDef):
                    checker = ClassChecker(
                        exclude_parameters=exclude_parameters, exclude_self=exclude_self
                    )
                else:
                    continue
                result = result and checker.check(
                    item,
                )
                checker.log_results(logger, filename=filename)
    return result


def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames", help="Files to be checked by annotation_checker.", nargs="+"
    )
    parser.add_argument(
        "--strict",
        help="If True and checks fails, exit the program with 1 code.",
        type=bool,
        default=False,
    )
    parser.add_argument(
        "--exclude_self",
        help="If True, omit type checking for the first parameter in methods.",
        type=bool,
        default=False,
    )
    parser.add_argument(
        "--exclude_files",
        help="Regex specifying which files should not be checked",
        type=str,
        default="",
    )
    parser.add_argument(
        "--exclude_parameters",
        help="Regex specifying which parameters should not be checked",
        type=str,
        default="",
    )
    args = parser.parse_args()
    return args


def filter_files(files: List[str], exclude_pattern: str) -> List[str]:
    """
    Filters the list of files passed by pre-commit hook to exclude files by a regex.
    Returns only filenames ending with .py
    Parameters
    ----------
        files (List[str]): Files to be checked
        exclude_pattern (str): Regex specifying which parameters should not be checked

    Returns
    -------
        List(str)
            list of files ending with .py and not excluded by the pattern
    """
    result = []
    for filename in files:
        if not exclude_pattern or not re.match(exclude_pattern, filename):
            if filename.endswith(".py"):
                result.append(filename)
    return result


def main() -> None:
    """Reads the command line arguments and runs the annotation_checker"""
    logger.setLevel(logging.INFO)
    args = parse_arguments()
    files = filter_files(files=args.filenames, exclude_pattern=args.exclude_files)
    logger.debug("Files: %s", files)
    exit_code = 1 - check_annotated(
        files,
        exclude_parameters=args.exclude_parameters,
        exclude_self=args.exclude_self,
    )
    if args.strict and exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
