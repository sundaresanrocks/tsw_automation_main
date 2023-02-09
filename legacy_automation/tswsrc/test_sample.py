import unittest

import pytest

@pytest.mark.parametrize(argnames="input,expected",
                         argvalues=[("3+5", 8),
                                    ("2+4", 6),
                                    ("6*9", 54)],
                         ids=["a", "b", 1])
def test_eval(input, expected):
    assert eval(input) == expected


def test_pass():
    assert True


class TestClassSample(unittest.TestCase):
    def test_pass(self):
        assert True

    @unittest.skip('Skip function')
    def test_skipped(self, value):
        """Sample pass test"""

    def test_fail(self):
        """Sample failed test"""
        raise AssertionError('x')

    def test_err(self):
        """Sample error test"""
        raise Exception('err')
