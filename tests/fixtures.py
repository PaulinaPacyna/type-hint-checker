from pytest import fixture


@fixture
def mixed():
    return "def f1(a, b: int):\n    return 5"
