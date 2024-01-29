import argparse
import re
import sys
from typing import List
import logging

from type_hint_checker.checkers import FunctionChecker, ClassChecker
from type_hint_checker.file_parser import FileParser

logger = logging.getLogger("type_hint_checker")
logging.basicConfig()


def check_type_hints(
    file_list: List[str],
    exclude_parameters: str = "^self$",
    exclude_by_name: str = "",
    ignore_comment: str = "no-check",
) -> bool:
    """
    Iterates through the list of file paths, parses the files and checks if all
    functions and classes in the files have type hints.
    Parameters
    ----------
        file_list: List[str] - Filenames to be checked by
        exclude_parameters: str - regex specifying which parameters should not be
                            checked
        exclude_by_name: str - Regex specifying names of functions, methods and classes
                            that should not be checked
        ignore_comment : str - if this phrase appears in the comment, the item is
                                not checked for type hints presence
    Returns
    ----------
        True if all files have type hints.
    """
    result = True
    for filename in file_list:
        file = FileParser(
            filename,
            excluded_names=exclude_by_name,
            ignore_comment=ignore_comment,
        )
        function_checker = FunctionChecker(exclude_parameters=exclude_parameters)
        class_checker = ClassChecker(exclude_parameters=exclude_parameters)

        for function in file.functions:
            result = function_checker.check(function) and result
            function_checker.log_results(logger, filename=filename)
        for class_ in file.classes:
            result = class_checker.check(class_) and result
            class_checker.log_results(logger, filename=filename)
    return result


def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames", help="Files to be checked by type_hint_checker.", nargs="+"
    )
    parser.add_argument(
        "--exit_zero",
        action="store_true",
        help="If this flag is checked, the program always exits with 0 (success) code.",
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
        default="^self$",
    )
    parser.add_argument(
        "--exclude_by_name",
        help="Regex specifying names of functions, methods and classes that should not "
        "be checked",
        type=str,
        default="",
    )
    parser.add_argument(
        "--log-level",
        help="Controls how the amount of log messages",
        type=str,
        default="INFO",
        choices=["INFO", "DEBUG"],
    )
    parser.add_argument(
        "--ignore_comment",
        help="If this phrase appears in the comment, the item is excluded. Default : "
        "'no-check'",
        type=str,
        default="no-check",
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
        if not exclude_pattern or not re.search(exclude_pattern, filename):
            if filename.endswith(".py"):
                result.append(filename)
    return result


def main() -> None:
    """Reads the command line arguments and runs the type_hint_checker"""
    args = parse_arguments()
    logger.setLevel(args.log_level)
    logger.debug(vars(args))
    files = filter_files(files=args.filenames, exclude_pattern=args.exclude_files)
    logger.debug("Files: %s", files)
    exit_code = 1 - check_type_hints(
        files,
        exclude_parameters=args.exclude_parameters,
        exclude_by_name=args.exclude_by_name,
        ignore_comment=args.ignore_comment,
    )
    if not args.exit_zero and exit_code:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
