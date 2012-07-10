import unittest
from steward import Component, Field, FieldComp, Error


class A(Component):
    a = Field()


class B(Component):
    a = FieldComp(A)


class C(Component):
    a = FieldComp(A, default=None)


class D(Component):
    a = FieldComp(A, default=A(a="unique"))


class TestCompo(unittest.TestCase):
    def test_ctor(self):
        a = A(a=1)
        b = B(a=a)
        self.assertEqual(1, b.a.a)
        self.assertEqual(1, b._dict_['a']['a'])

    def test_as_dict(self):
        r = B(a=A(a=2))
        self.assertEqual({'a': {'a': 2}}, r.as_dict())
        self.assertIs(r.a.as_dict(), r.as_dict()['a'])

    def test_from_dict(self):
        d = {'a': {'a': 'zzz'}}
        r = B.from_dict(d)
        self.assertEqual(d, r.as_dict())
        self.assertIsInstance(r.a, A)
        self.assertIsInstance(r.__dict__['a'], A)
        self.assertIsInstance(r._dict_['a'], dict)
        self.assertEqual('zzz', r.a.a)
        self.assertIs(r.a.as_dict(), r.as_dict()['a'])

    def test_nested(self):
        d = {'a': {'a': 'zzz'}}
        r = B.from_dict(d)
        r.a.a = 'yyy'
        self.assertEqual('yyy', r.a.a)
        self.assertEqual('yyy', r.a._dict_['a'])
        self.assertEqual('yyy', r._dict_['a']['a'])

    def test_setter(self):
        d = {'a': {'a': 'zzz'}}
        r = B.from_dict(d)
        a = A(a='yyy')
        r.a = a
        self.assertEqual('yyy', r.a.a)
        self.assertEqual('yyy', r.a._dict_['a'])
        self.assertEqual('yyy', r._dict_['a']['a'])
        self.assertIs(r.a.as_dict(), r.as_dict()['a'])
        self.assertIs(a.as_dict(), r.as_dict()['a'])

    def test_default(self):
        r = C()
        self.assertIsNone(r.a)
        self.assertIs(C.a.default, r.a)
        self.assertEqual({'a': None}, r.as_dict())
        r1 = D()
        self.assertEqual('unique', r1.a.a)
        self.assertIs(D.a.default, r1.a)
        self.assertEqual({'a': {'a': 'unique'}}, r1.as_dict())
