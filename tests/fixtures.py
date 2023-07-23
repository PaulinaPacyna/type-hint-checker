import pathlib

from pytest import fixture


@fixture
def variable_def(tmp_path: pathlib.Path):
    CONTENT = "def f1(a, b: int):\n    return 5"
    file = (tmp_path/"file.py")
    file.write_text(CONTENT, encoding="utf-8")
    return file
