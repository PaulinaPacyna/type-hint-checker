import ast
from abc import ABC, abstractmethod
from logging import Logger
from typing import List, Optional


class Checker(ABC):
    def __init__(self) -> None:
        self.errors = []  # TODO: make this field private

    @abstractmethod
    def check(self) -> bool:
        """
        Returns True if a given function/method is type-annotated according to settings.
        Returns
        -------
            Bool
        """
        pass

    def log_results(self, logger: Logger, filename: Optional[str] = None) -> None:
        """
        Displays a log message for each incorrectly annotated function or method.
        Parameters
        ----------
        logger : Logger
            logger object that displays the message.
        filename :
            If provided, the filename will be prepended to the log message
        Returns
        -------
            None
        """
        prefix = ""
        if filename:
            prefix = f"{filename}: "
        for error in self.errors:
            logger.info(f"{prefix}{error}")


class FunctionChecker(Checker):
    """Checks if a function is correctly type-annotated."""

    def __init__(self, function: ast.FunctionDef, exclude_args: List[str] = ()) -> None:
        super().__init__()
        self.function: ast.FunctionDef = function
        self.exclude_args = exclude_args  # TODO: move to parent class

    def check(self) -> bool:
        """
        Checks that the function is annotated (arguments and return type).
        Returns
        -------
        bool
            True if correctly annotated
        """
        self.__check_args()
        self.__check_return()
        return not bool(self.errors)

    def __check_args(self) -> None:
        """Check that the arguments of a function are correctly type-annotated."""
        for argument in self.function.args.args:
            if not argument.annotation:
                if argument.arg not in self.exclude_args:
                    self.errors.append(
                        f"Missing annotation for argument {argument.arg} "
                        f"(function {self.function.name}), line {self.function.lineno}"
                    )

    def __check_return(self) -> None:
        """Check that the function return type is provided."""
        if not self.function.returns:
            self.errors.append(
                f"Missing return annotation for function {self.function.name}, "
                f"line {self.function.lineno}"
            )


class ClassChecker(Checker):
    """
    Checks if all methods in a given class are correctly type-annotated.
    """

    def __init__(self, class_: ast.ClassDef, exclude_args: List[str] = ()) -> None:
        super().__init__()
        self.exclude_args = exclude_args
        self.class_ = class_

    def check(self) -> bool:
        """
        Checks if all methods in a given class are correctly type-annotated.
        Returns
        -------
        bool
            True if all methods are correctly type-annotated.
        """
        result = True
        for method in self.class_.body:
            if isinstance(method, ast.FunctionDef):
                function_checker = FunctionChecker(
                    method, exclude_args=self.exclude_args
                )
                result = result and function_checker.check()
                self.errors += function_checker.errors
        return result
