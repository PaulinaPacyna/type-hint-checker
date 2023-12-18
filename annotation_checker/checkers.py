import ast
import re
from abc import ABC, abstractmethod
from logging import Logger
from typing import List, Optional, Union


class Checker(ABC):
    """Checks if an object is correctly type-annotated.
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_self (bool): if True, omit type checking for the first parameter in
                                method
        exclude_by_name: str - Regex specifying names of functions, methods and classes
                                that should not be checked
    """

    def __init__(
        self,
        exclude_parameters: str = "",
        exclude_self: bool = False,
        exclude_by_name: str = "",
    ) -> None:
        self._errors = []
        self._exclude_parameters = exclude_parameters
        self._exclude_self = exclude_self
        self._exclude_by_name = exclude_by_name

    @abstractmethod
    def check(self, item: Union[ast.FunctionDef, ast.ClassDef]) -> bool:
        """
        Returns True if a given function/method is type-annotated according to settings.
        Parameters
        ----------
            item (Union[ast.FunctionDef, ast.ClassDef]): the object to be checked
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

    def _check_if_name_not_excluded(self, name: str) -> bool:
        """
        Checks if the function or class should be checked
        Parameters
        ----------
        name (str): name of the function or class

        Returns
        -------
            bool - False if the object should not be checked
        """
        return not self._exclude_by_name or not re.search(self._exclude_by_name, name)


class FunctionChecker(Checker):
    """Checks if a function is correctly type-annotated.
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_self (bool): if True, omit type checking for the first parameter in
                                method
        exclude_by_name: str - Regex specifying names of functions, methods and classes
                                that should not be checked
    """

    def __init__(
        self,
        exclude_parameters: str = "",
        exclude_self: bool = False,
        exclude_by_name: str = "",
    ) -> None:
        super().__init__(
            exclude_parameters=exclude_parameters,
            exclude_self=exclude_self,
            exclude_by_name=exclude_by_name,
        )

    def check(self, item: ast.FunctionDef) -> bool:
        """
        Checks that the function is annotated (arguments and return type).
        Parameters
        ----------
            item (ast.FunctionDef): the function to be checked
        Returns
        -------
        bool
            True if correctly annotated
        """
        if self._check_if_name_not_excluded(item.name):
            self.__check_args(item)
            self.__check_return(item)
        return not bool(self._errors)

    def __check_args(self, function: ast.FunctionDef) -> None:
        """Check that the arguments of a function are correctly type-annotated.
        Parameters
        ----------
            function (ast.FunctionDef): the function to be checked
        """
        args = function.args.args
        if self._exclude_self:
            args = args[1:]
        for argument in args:
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
        return not self._exclude_parameters or not re.search(
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
        exclude_by_name: str - Regex specifying names of functions, methods and classes
                                that should not be checked
    """

    def __init__(
        self,
        exclude_parameters: List[str] = (),
        exclude_self: bool = False,
        exclude_by_name: str = "",
    ) -> None:
        super().__init__(
            exclude_parameters=exclude_parameters,
            exclude_self=exclude_self,
            exclude_by_name=exclude_by_name,
        )

    def check(self, item: ast.ClassDef) -> bool:
        """
        Checks if all methods in a given class are correctly type-annotated.
        Parameters
        ----------
            item (ast.FunctionDef): the class to be checked
        Returns
        -------
        bool
            True if all methods are correctly type-annotated.
        """
        result = True
        if not self._check_if_name_not_excluded(item.name):
            return result
        for method in item.body:
            if isinstance(method, ast.FunctionDef):
                function_checker = FunctionChecker(
                    exclude_self=self._exclude_self,
                    exclude_parameters=self._exclude_parameters,
                    exclude_by_name=self._exclude_by_name,
                )
                result = function_checker.check(method) and result
                self._errors += function_checker.get_errors()
        return result
