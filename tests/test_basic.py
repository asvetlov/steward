import unittest
from steward import Component, Field, Error


class A(Component):
    a = Field()
    b = Field()
    c = Field(default='zzz')
    d = Field(maker=lambda: 'ddd')


class TestBasic(unittest.TestCase):
    def test_meta(self):
        fields = {'a', 'b', 'c', 'd'}
        self.assertEqual(fields, set(A._fields_.keys()))
        self.assertEqual(fields, A._names_)

    def test_ctor(self):
        a = A(a=1, b='b')
        self.assertEqual(1, a.a)
        self.assertEqual('b', a.b)

        with self.assertRaisesRegexp(Error, "Extra params: 'z'"):
            A(z=1)

        with self.assertRaisesRegexp(Error, "Missing params: 'b'"):
            A(a=1)

    def test_get_set(self):
        a = A(a=1, b='xxx')
        self.assertEqual(1, a.a)
        self.assertEqual('xxx', a.b)
        a.a = 3
        a.b = 'yyyy'
        self.assertEqual(3, a.a)
        self.assertEqual('yyyy', a.b)

    def test_default(self):
        a = A(a=1, b='bbb')
        self.assertEqual('zzz', a.c)

    def test_maker(self):
        a = A(a=1, b='bbb')
        self.assertEqual('ddd', a.d)
