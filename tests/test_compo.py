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
        self.assertEqual(1, b._plain_['a']['a'])

    def test_as_plain(self):
        r = B(a=A(a=2))
        self.assertEqual({'a': {'a': 2}}, r.as_plain())
        self.assertIs(r.a.as_plain(), r.as_plain()['a'])

    def test_from_plain(self):
        d = {'a': {'a': 'zzz'}}
        r = B.from_plain(d)
        self.assertEqual(d, r.as_plain())
        self.assertIsInstance(r.a, A)
        self.assertIsInstance(r.__dict__['a'], A)
        self.assertIsInstance(r._plain_['a'], dict)
        self.assertEqual('zzz', r.a.a)
        self.assertIs(r.a.as_plain(), r.as_plain()['a'])

    def test_nested(self):
        d = {'a': {'a': 'zzz'}}
        r = B.from_plain(d)
        r.a.a = 'yyy'
        self.assertEqual('yyy', r.a.a)
        self.assertEqual('yyy', r.a._plain_['a'])
        self.assertEqual('yyy', r._plain_['a']['a'])

    def test_setter(self):
        d = {'a': {'a': 'zzz'}}
        r = B.from_plain(d)
        a = A(a='yyy')
        r.a = a
        self.assertEqual('yyy', r.a.a)
        self.assertEqual('yyy', r.a._plain_['a'])
        self.assertEqual('yyy', r._plain_['a']['a'])
        self.assertIs(r.a.as_plain(), r.as_plain()['a'])
        self.assertIs(a.as_plain(), r.as_plain()['a'])

    def test_default(self):
        r = C()
        self.assertIsNone(r.a)
        self.assertIs(C.a.default, r.a)
        self.assertEqual({'a': None}, r.as_plain())
        r1 = D()
        self.assertEqual('unique', r1.a.a)
        self.assertIs(D.a.default, r1.a)
        self.assertEqual({'a': {'a': 'unique'}}, r1.as_plain())

    def test_assign_to_default(self):
        r = C()
        r.a = A(a='value')
        self.assertEqual({'a': {'a': 'value'}}, r.as_plain())

    def test_override_default(self):
        r = C(a=A(a='value'))
        self.assertEqual({'a': {'a': 'value'}}, r.as_plain())
        r = C(a=None)
        self.assertEqual({'a': None}, r.as_plain())
