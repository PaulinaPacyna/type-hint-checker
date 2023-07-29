import ast
from abc import ABC, abstractmethod
from logging import Logger
from typing import List, Optional


class Checker(ABC):
    def __init__(self):
        self.errors = []

    @abstractmethod
    def check(self):
        pass

    def log_results(self, logger: Logger, filename: Optional[str] = None):
        prefix = ""
        if filename:
            prefix = f"{filename}: "
        for error in self.errors:
            logger.info(f"{prefix}{error}")


class FunctionChecker(Checker):
    def __init__(self, function: ast.FunctionDef, exclude_args: List[str] = ()):
        super().__init__()
        self.function: ast.FunctionDef = function
        self.exclude_args = exclude_args

    def check(self) -> bool:
        self.__check_args()
        self.__check_return()
        return bool(self.errors)

    def __check_args(self) -> None:
        for argument in self.function.args.args:
            if not argument.annotation:
                if argument.arg not in self.exclude_args:
                    self.errors.append(
                        f"Missing annotation for argument {argument.arg} "
                        f"(function {self.function.name}), line {self.function.lineno}"
                    )

    def __check_return(self):
        if not self.function.returns:
            self.errors.append(
                f"Missing return annotation for function {self.function.name}, "
                f"line {self.function.lineno}"
            )


class ClassChecker(Checker):
    def __init__(self, class_: ast.ClassDef, exclude_args: List[str] = ()):
        super().__init__()
        self.exclude_args = exclude_args
        self.class_ = class_

    def check(self):
        result = False
        for method in self.class_.body:
            if isinstance(method, ast.FunctionDef):
                function_checker = FunctionChecker(
                    method, exclude_args=self.exclude_args
                )
                result = result or function_checker.check()
                self.errors += function_checker.errors
        return result
