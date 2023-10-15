import ast
import re
from abc import ABC, abstractmethod
from logging import Logger
from typing import List, Optional


class Checker(ABC):
    """Checks if an object is correctly type-annotated.
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_self (bool): if True, omit type checking for the first parameter in
                                method
    """

    def __init__(
        self, exclude_parameters: str = "", exclude_self: bool = False
    ) -> None:
        self._errors = []
        self._exclude_parameters = exclude_parameters
        self._exclude_self = exclude_self

    @abstractmethod
    def check(self, source: str) -> bool:
        """
        Returns True if a given function/method is type-annotated according to settings.
        Parameters
        ----------
            source (str): string containing the source of the object to be checked
        Returns
        -------
            Bool
        """

    def log_results(self, logger: Logger, filename: Optional[str] = None) -> None:
        """
        Displays a log message for each incorrectly annotated function or method.
        Parameters
        ----------
            logger (Logger): logger object that displays the message.
            filename (Optional[str]): If provided, the filename will be
                        prepended to the log message
        Returns
        -------
            None
        """
        prefix = ""
        if filename:
            prefix = f"{filename}: "
        for error in self._errors:
            logger.info(f"{prefix}{error}")

    def get_errors(self) -> List[str]:
        """
        Returns list of string describing the errors detected.
        """
        return self._errors


class FunctionChecker(Checker):
    """Checks if a function is correctly type-annotated.
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_self (bool): if True, omit type checking for the first parameter in
                                method
    """

    def __init__(
        self, exclude_parameters: str = "", exclude_self: bool = False
    ) -> None:
        super().__init__(
            exclude_parameters=exclude_parameters, exclude_self=exclude_self
        )

    def check(self, source: str) -> bool:
        """
        Checks that the function is annotated (arguments and return type).
        Parameters
        ----------
            source (str): string containing the source of the function to be checked
        Returns
        -------
        bool
            True if correctly annotated
        """
        self.__check_args(source)
        self.__check_return(source)
        return not bool(self._errors)

    def __check_args(self, function: ast.FunctionDef) -> None:
        """Check that the arguments of a function are correctly type-annotated.
        Parameters
        ----------
            function (str): string containing the source of the function to be checked
        """
        args = function.args
        if self._exclude_self:
            args = args[1:]
        for argument in args.args:
            if not argument.annotation:
                if self.__check_if_not_excluded(argument.arg):
                    self._errors.append(
                        f"Missing annotation for argument {argument.arg} "
                        f"(function {function.name}), line {function.lineno}"
                    )

    def __check_if_not_excluded(self, argument: str) -> bool:
        """Returns False if the argument should not be checked.
        Parameters
        ----------
            argument (str): - the arguments' name
        Returns
        ---------
            bool
        """
        return not self._exclude_parameters or not re.match(
            self._exclude_parameters, argument
        )

    def __check_return(self, function: ast.FunctionDef) -> None:
        """Check that the function return type is provided.
        Parameters
        ----------
            function (ast.FunctionDef): string containing the source of the function to
                                        be checked
        """
        if not function.returns:
            self._errors.append(
                f"Missing return annotation for function {function.name}, "
                f"line {function.lineno}"
            )


class ClassChecker(Checker):
    """
    Checks if all methods in a given class are correctly type-annotated..
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_self (bool): if True, omit type checking for the first parameter in
                                methods
    """

    def __init__(
        self, exclude_parameters: List[str] = (), exclude_self: bool = False
    ) -> None:
        super().__init__(
            exclude_parameters=exclude_parameters, exclude_self=exclude_self
        )

    def check(self, source: ast.ClassDef) -> bool:
        """
        Checks if all methods in a given class are correctly type-annotated.
        Parameters
        ----------
            source (str): string containing the ast.source of the class to be checked
        Returns
        -------
        bool
            True if all methods are correctly type-annotated.
        """
        result = True
        for method in source.body:
            if isinstance(method, ast.FunctionDef):
                function_checker = FunctionChecker(exclude_self=self._exclude_self)
                result = result and function_checker.check(method)
                self._errors += function_checker.get_errors()
        return result
