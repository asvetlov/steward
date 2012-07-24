import unittest

from steward import FieldComp, Component, Forward


A = Forward()

class A(Component, forward=A):
    next = FieldComp(A, default=None)


class TestForward(unittest.TestCase):
    def test_class(self):
        self.assertIs(A, A.next.type)
