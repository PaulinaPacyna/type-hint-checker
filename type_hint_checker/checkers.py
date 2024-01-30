import ast
import re
from abc import ABC, abstractmethod
from logging import Logger
from typing import List, Optional, Union


class Checker(ABC):
    """Checks if an object is chas type hints.
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_by_name: str - Regex specifying names of functions, methods and classes
                                that should not be checked
    """

    def __init__(
        self,
        exclude_parameters: str = "^self$",
        exclude_by_name: str = "",
    ) -> None:
        self._errors = []
        self._exclude_parameters = exclude_parameters
        self._exclude_by_name = exclude_by_name

    @abstractmethod
    def check(self, item: Union[ast.FunctionDef, ast.ClassDef]) -> bool:
        """
        Returns True if a given function/method has type hints.
        Parameters
        ----------
            item (Union[ast.FunctionDef, ast.ClassDef]): the object to be checked
        Returns
        -------
            Bool
        """

    def log_results(self, logger: Logger, filename: Optional[str] = None) -> None:
        """
        Displays a log message for each function or method with type hints.
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
    """Checks if a function is has type hints.
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_by_name: str - Regex specifying names of functions, methods and classes
                                that should not be checked
    """

    def __init__(
        self,
        exclude_parameters: str = "",
        exclude_by_name: str = "",
    ) -> None:
        super().__init__(
            exclude_parameters=exclude_parameters,
            exclude_by_name=exclude_by_name,
        )

    def check(self, item: ast.FunctionDef) -> bool:
        """
        Checks that the function has type hints (parameters and return type).
        Parameters
        ----------
            item (ast.FunctionDef): the function to be checked
        Returns
        -------
        bool
            True if type hints are present
        """
        self.__check_parameters(item)
        self.__check_return(item)
        return not bool(self._errors)

    def __check_parameters(self, function: ast.FunctionDef) -> None:
        """Check that the parameters of a function has type hints.
        Parameters
        ----------
            function (ast.FunctionDef): the function to be checked
        """
        parameters = function.args.args
        for parameter in parameters:
            if not parameter.annotation:
                if self.__check_if_param_should_be_checked(parameter.arg):
                    self._errors.append(
                        f"Missing type hint for parameter {parameter.arg} "
                        f"(function {function.name}), line {function.lineno}"
                    )

    def __check_if_param_should_be_checked(self, parameter: str) -> bool:
        """Returns True if the parameter should be checked.
        Parameters
        ----------
            parameter (str): - the parameters' name
        Returns
        ---------
            bool
        """
        return not self._exclude_parameters or not re.search(
            self._exclude_parameters, parameter
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
                f"Missing return type hint for function {function.name}, "
                f"line {function.lineno}"
            )


class ClassChecker(Checker):
    """
    Checks if all methods in a given class has type hints.
    Parameters
    ----------
        exclude_parameters (str): regex specifying which parameters should not be
                                checked
        exclude_by_name: str - Regex specifying names of functions, methods and classes
                                that should not be checked
    """

    def __init__(
        self,
        exclude_parameters: List[str] = (),
        exclude_by_name: str = "",
    ) -> None:
        super().__init__(
            exclude_parameters=exclude_parameters,
            exclude_by_name=exclude_by_name,
        )

    def check(self, item: ast.ClassDef) -> bool:
        """
        Checks if all methods in a given class has type hints.
        Parameters
        ----------
            item (ast.FunctionDef): the class to be checked
        Returns
        -------
        bool
            True if all methods have type hints.
        """
        result = True
        for method in item.body:
            if isinstance(method, ast.FunctionDef):
                function_checker = FunctionChecker(
                    exclude_parameters=self._exclude_parameters,
                    exclude_by_name=self._exclude_by_name,
                )
                result = function_checker.check(method) and result
                self._errors += function_checker.get_errors()
        return result
