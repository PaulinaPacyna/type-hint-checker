from annotation_checker.main import check_annotated
from tests.fixtures import *


def test_check_annotated(variable_def):
    assert check_annotated([variable_def])
