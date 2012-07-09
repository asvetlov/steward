import unittest
from steward import Component, Field, Error


class A(Component):
    a = Field()
    b = Field()
    c = Field(default='zzz')


class TestBasic(unittest.TestCase):
    def test_meta(self):
        fields = {'a', 'b', 'c'}
        self.assertEqual(fields, set(A._fields_.keys()))
        self.assertEqual(fields, A._names_)

        self.assertIsInstance(A.a, Field)

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
        self.assertEqual(1, a.__dict__['a'])
        self.assertEqual(1, a._dict_['a'])
        a.a = 3
        a.b = 'yyyy'
        self.assertEqual(3, a.a)
        self.assertEqual('yyyy', a.b)

    def test_default(self):
        a = A(a=1, b='bbb')
        self.assertEqual('zzz', a.c)
        self.assertEqual('zzz', a.__dict__['c'])
        self.assertEqual('zzz', a._dict_['c'])

    def test_from_dict(self):
        dct = {'a': 1, 'b': 2, 'c': 3}
        r = A.from_dict(dct)
        self.assertIsInstance(r, A)
        self.assertEqual(1, r.a)
        self.assertEqual(2, r.b)
        self.assertEqual(3, r.c)

    def test_as_dict(self):
        a = A(a=5, b=6)
        self.assertEqual({'a': 5, 'b': 6, 'c': 'zzz'}, a.as_dict())
