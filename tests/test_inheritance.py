from steward import Field, Component

import unittest


class A(Component):
    a = Field()


class B(A):
    b = Field()


class TestInheritance(unittest.TestCase):
    def test_class(self):
        self.assertEqual({'a'}, A._names_)

    def test_inherites(self):
        self.assertEqual({'a', 'b'}, B._names_)

    def test_simple(self):
        b = B(a=1, b=2)
        self.assertEqual(1, b.a)
        self.assertEqual(2, b.b)
