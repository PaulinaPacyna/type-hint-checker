import argparse
from typing import List
import logging
import ast

from annotation_checker.checkers import FunctionChecker, ClassChecker

logger = logging.getLogger("annotation_checker")
logging.basicConfig()


def check_annotated(file_list: List[str], exclude_self: bool = False) -> bool:
    """
    Iterates through the list of file paths, parses the files and checks if all functions and classes in the files are
    correctly type-annotated.
    """
    result = True
    exclude_args = []  # TODO: add as argument
    if exclude_self:
        exclude_args.append("self")
    for filename in file_list:
        with open(filename, "r") as file:
            content = file.read()
            body = ast.parse(content).body
            for item in body:
                if isinstance(item, ast.FunctionDef):
                    checker = FunctionChecker(item)
                elif isinstance(item, ast.ClassDef):
                    checker = ClassChecker(item, exclude_args=exclude_args)
                else:
                    continue
                result = result and checker.check()
                checker.log_results(logger)
    return result


def parse_arguments() -> argparse.Namespace:
    """
    Parses command line arguments.
    Returns
    -------
        Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames", help="Files to be checked by annotation_checker.", nargs="+"
    )
    parser.add_argument(
        "--strict",
        help="If True and checks failes, exit the program with 1 code.",
        type=bool,
        default=False,
    )
    parser.add_argument(
        "--exclude_self",
        help="If True, omit type checking for parameter `self` in methods.",
        type=bool,
        default=False,
    )
    args = parser.parse_args()
    return args


def main() -> None:
    """Reads the command lines arguments and runs the annotation_checker"""
    logger.setLevel(logging.INFO)
    args = parse_arguments()
    logger.debug("Files: %s", args.filenames)
    exit_code = 1 - check_annotated(args.filenames, exclude_self=args.exclude_self)
    if args.strict and exit_code:
        exit(exit_code)


if __name__ == "__main__":
    main()
