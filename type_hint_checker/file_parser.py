import ast
import re
from tokenize import tokenize, COMMENT
from typing import List

from type_hint_checker.exceptions import IncorrectFileException


class FileParser:  # pylint: disable=too-few-public-methods
    """
    File with its AST, functions, classes and exclusions by comments
    Parameters
    ----------
        filename : str - path to the file
        excluded_names : str - regex specifying which functions and classes should be
                                omitted
        ignore_comment : str - if this phrase appears in the comment, the item is
                                excluded
    """

    def __init__(
        self,
        filename: str,
        excluded_names: str = "",
        ignore_comment: str = "no-check",
    ) -> None:
        self.__ignore_comment = ignore_comment
        self.__excluded_names = excluded_names
        self.__filename = filename
        self.__body = self.__get_body()
        self.__excluded_lines = self.__get_excluded_lines()
        self.functions = self.__get_functions()
        self.classes = self.__get_classes()

    def __get_body(self) -> List[ast.AST]:
        """Parse the file into an Abstract Syntax Tree
        Returns
        -------
            List[ast.AST] - list of ast items from the file"""
        with open(self.__filename, "r", encoding="utf-8") as file:
            source = file.read()
        try:
            body = ast.parse(source).body
        except SyntaxError as exc:
            raise IncorrectFileException(
                f"File could not be parsed: {self.__filename}"
            ) from exc
        return body

    def __get_functions(self) -> List[ast.FunctionDef]:
        """Return functions defined in the file if not excluded
        Returns
        -------
            List[ast.FunctionDef] - list of ast.FunctionDefs from the file"""
        return [
            item
            for item in self.__body
            if isinstance(item, ast.FunctionDef)
            and not self.__is_excluded_by_comment(item)
            and not self.__is_excluded_by_name(item.name)
        ]

    def __get_classes(self) -> List[ast.ClassDef]:
        """Return classes defined in the file if not excluded
        Returns
        -------
            List[ast.ClassDef] - list of ast.ClassDefs from the file
        """
        return [
            item
            for item in self.__body
            if isinstance(item, ast.ClassDef)
            and not self.__is_excluded_by_comment(item)
            and not self.__is_excluded_by_name(item.name)
        ]

    def __get_excluded_lines(self) -> List[int]:
        """Return list of lines that are excluded from checking
        Returns
        ------
            List[int] - lines that are excluded

        """
        result = []
        with open(self.__filename, "rb") as file:
            tokenized = tokenize(file.readline)
            for item in tokenized:
                if item.exact_type == COMMENT:
                    if self.__ignore_comment in item.line:
                        result.append(item.start[0])
        return result

    def __is_excluded_by_comment(self, item: ast.AST) -> bool:
        """Return True if the item should be ommited
        Parameters
        _______
            item: ast item with fields .lineno and .end_lineno

        Returns
        -------
            bool - False if the object should not be checked"""
        for line in self.__excluded_lines:
            if item.lineno <= line <= item.end_lineno:
                return True
        return False

    def __is_excluded_by_name(self, name: str) -> bool:
        """
        Checks if the function or class should be checked
        Parameters
        ----------
        name (str): name of the function or class

        Returns
        -------
            bool - False if the object should not be checked
        """
        return self.__excluded_names and re.search(self.__excluded_names, name)
