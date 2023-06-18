import argparse
from typing import List
import logging
import ast

from annotation_checker.checkers import FunctionChecker, ClassChecker

logger = logging.getLogger("annotation-checker")
logging.basicConfig()


def check_annotated(file_list: List[str], exclude_self: bool = False) -> bool:
    number_or_errors = 0
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
                number_or_errors = number_or_errors + checker.check()
                checker.log_results(logger)
    return bool(number_or_errors)


def main():
    logger.setLevel(logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="+")
    parser.add_argument("--strict", type=bool, default=False)
    parser.add_argument("--exclude_self", type=bool, default=False)
    args = parser.parse_args()
    logger.debug("Files: %s", args.filenames)
    exit_code = check_annotated(args.filenames, exclude_self=args.exclude_self)
    if args.strict and exit_code:
        exit(exit_code)


if __name__ == "__main__":
    main()
