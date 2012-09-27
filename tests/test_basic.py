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
        self.assertEqual({'a', 'b', 'c'}, set(a._plain_))
        self.assertEqual({'a', 'b', 'c', '_plain_'}, set(a.__dict__))
        self.assertEqual({'a': 1, 'b': 'b', 'c': 'zzz'}, a._plain_)
        self.assertEqual(1, a.a)
        self.assertEqual('b', a.b)

        with self.assertRaisesRegex(Error, "Extra params: 'z'"):
            A(z=1)

        with self.assertRaisesRegex(Error, "Missing params: 'b'"):
            A(a=1)

    def test_get_set(self):
        a = A(a=1, b='xxx')
        self.assertEqual(1, a.a)
        self.assertEqual('xxx', a.b)
        self.assertEqual(1, a.__dict__['a'])
        self.assertEqual(1, a._plain_['a'])
        a.a = 3
        a.b = 'yyyy'
        self.assertEqual(3, a.a)
        self.assertEqual('yyyy', a.b)

    def test_default(self):
        a = A(a=1, b='bbb')
        self.assertEqual('zzz', a.c)
        self.assertEqual('zzz', a.__dict__['c'])
        self.assertEqual('zzz', a._plain_['c'])

    def test_from_plain(self):
        dct = {'a': 1, 'b': 2, 'c': 3}
        r = A.from_plain(dct)
        self.assertIsInstance(r, A)
        self.assertEqual({'_plain_': dct}, r.__dict__)
        self.assertEqual(1, r.a)
        self.assertEqual(2, r.b)
        self.assertEqual(3, r.c)

    def test_as_plain(self):
        a = A(a=5, b=6)
        self.assertEqual({'a': 5, 'b': 6, 'c': 'zzz'}, a.as_plain())

    def test_const(self):
        class C(Component):
            a = Field()
            b = Field(const=True)
        c = C(a=1, b=2)
        self.assertEqual(1, c.a)
        self.assertEqual(2, c.b)
        with self.assertRaises(AttributeError):
            c.b = 3

    def test_default_const(self):
        class A(Component):
            a = Field(const=True, default='a')
        a = A()
        self.assertEqual('a', a.a)
        with self.assertRaises(AttributeError):
            a.a = 'b'

    def test_clone(self):
        class C(Component):
            a = Field()
            b = Field(const=True)
        a = C(a=1, b=2)
        self.assertEqual(1, a.a)
        self.assertEqual(2, a.b)
        b = a.clone()
        self.assertEqual(1, b.a)
        self.assertEqual(2, b.b)
        self.assertIs(C, a.__class__)
        self.assertIs(C, b.__class__)

    def test_clone_update_mutable_field(self):
        class C(Component):
            a = Field()
            b = Field(const=True)
        a = C(a=1, b=2)
        b = a.clone(a=3)
        self.assertEqual(3, b.a)
        self.assertEqual(2, b.b)

    def test_clone_update_immutable_field(self):
        class C(Component):
            a = Field()
            b = Field(const=True)
        a = C(a=1, b=2)
        b = a.clone(b=3)
        self.assertEqual(1, b.a)
        self.assertEqual(3, b.b)

    def test_clone_cannot_update_unknown_field(self):
        class C(Component):
            a = Field()
            b = Field(const=True)
        a = C(a=1, b=2)
        with self.assertRaises(Error):
            a.clone(unknown=3)

    def test_cannot_specify_both_defaut_and_maker(self):
        with self.assertRaises(TypeError):
            Field(default=1, maker=int)

    def test_maker_should_be_callable(self):
        with self.assertRaises(TypeError):
            Field(maker=1)

    def test_maker(self):
        class C(Component):
            a = Field(maker=lambda: 'a')
        c = C()
        self.assertEqual('a', c.a)
