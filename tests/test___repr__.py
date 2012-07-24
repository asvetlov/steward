import unittest

from steward import Field, FieldComp, FieldDict, FieldList, Component


class A(Component):
    a = Field()


unbound = Field()
unbound_comp = FieldComp(A)
unbound_dct = FieldComp(A)
unbound_lst = FieldComp(A)


class B(Component):
    simple = Field()
    default = Field(default=123)
    comp = FieldComp(A)
    comp_with_default = FieldComp(A, default=A(a='a'))
    dct = FieldDict(A)
    lst = FieldList(A)


class Test___repr__(unittest.TestCase):
    def test_unbound(self):
        self.assertEqual('<Unbound>', repr(unbound))
        self.assertEqual('<Unbound>', repr(unbound_comp))
        self.assertEqual('<Unbound>', repr(unbound_dct))
        self.assertEqual('<Unbound>', repr(unbound_lst))

    def test_field(self):
        self.assertEqual("<Field 'simple'>", repr(B.simple))
        self.assertEqual("<Field 'default' default=123>", repr(B.default))

    def test_comp(self):
        self.assertEqual("<FieldComp 'comp'[{}.{}]>".format(A.__module__,
                                                            A.__name__),
                         repr(B.comp))
        exp = "<FieldComp 'comp_with_default'[{}.{}] default={!r}>".format(
            A.__module__, A.__name__, B.comp_with_default.default)
        self.assertEqual(exp,
                         repr(B.comp_with_default))
