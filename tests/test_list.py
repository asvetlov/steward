import unittest
from steward import Component, Field, FieldComp, FieldList, Error


class A(Component):
    a = Field()


class B(Component):
    a = FieldList(A)


class TestList(unittest.TestCase):
    def test_ctor(self):
        r = B()
        self.assertEqual(0, len(r.a))

    def test_from_dict(self):
        d = {'a': [{'a': 'a'},
                   {'a': 'b'},
                   {'a': 'c'}]}
        r = B.from_dict(d)
        self.assertEqual(3, len(r.a))
        self.assertIs(d, r.as_dict())
        self.assertIs(d['a'], r.a.as_list())
        self.assertEqual('a', r.a[0].a)
        self.assertEqual('c', r.a[2].a)

    def test_setitem(self):
        d = {'a': [{'a': 'a'},
                   {'a': 'b'}]}
        r = B.from_dict(d)
        self.assertEqual(2, len(r.a))
        r.a[0] = A(a='d')
        self.assertEqual(2, len(r.a))
        self.assertEqual('d', r.a[0].a)
        self.assertEqual({'a': [{'a': 'd'},
                                {'a': 'b'}]}, r.as_dict())

    def test_add_item(self):
        r = B()
        r.a.append(A(a='a'))
        self.assertEqual(1, len(r.a))
        self.assertEqual({'a': [{'a': 'a'}]}, r.as_dict())
        self.assertIs(r.as_dict()['a'], r.a.as_list())
        self.assertIs(r.as_dict()['a'][0], r.a.as_list()[0])

    def test_delitem(self):
        d = {'a': [{'a': 'a'},
                   {'a': 'b'}]}
        r = B.from_dict(d)
        self.assertEqual(2, len(r.a))
        del r.a[0]
        self.assertEqual(1, len(r.a))
        self.assertEqual({'a': [{'a': 'b'}]}, r.as_dict())
