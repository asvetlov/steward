import unittest
from steward import Component, Field, Error


class A(Component):
    a = Field()
    b = Field()


class TestBasic(unittest.TestCase):
    def test_meta(self):
        self.assertEqual({'a', 'b'}, set(A._fields_.keys()))
        self.assertEqual({'a', 'b'}, A._names_)

    def test_ctor(self):
        a = A(a=1, b='b')
        self.assertEqual(1, a.a)
        self.assertEqual('b', a.b)

        with self.assertRaisesRegexp(Error, "Extra params: 'z'"):
            A(z=1)

        with self.assertRaisesRegexp(Error, "Missing params: 'b'"):
            A(a=1)
