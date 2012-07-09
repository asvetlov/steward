from collections import OrderedDict


sentinel = object()


class Error(Exception):
    """Base error"""


class Field:
    name = None

    def __init__(self, *, default=sentinel):
        self.default = default

    def set_name(self, name):
        assert self.name is None, self.name
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        assert self.name
        ret = instance.__dict__.get(self.name, sentinel)
        if ret is sentinel:
            ret = self.getter(instance)
        instance.__dict__[self.name] = ret
        instance._dict_[self.name] = ret
        return ret

    def getter(self, instance):
        ret = instance._dict_.get(self.name, sentinel)
        if ret is sentinel and self.default is not sentinel:
            ret = self.default
        elif ret is sentinel:
            raise AttributeError("'{.name}' is not initialized".format(self))
        return ret

    def __set__(self, instance, value):
        assert self.name
        self.setter(instance, value)

    def setter(self, instance, value):
        instance._dict_[self.name] = value
        instance.__dict__[self.name] = value


class FieldComp(Field):
    def __init__(self, type):
        super().__init__(self)
        self.type = type

    def setter(self, instance, value):
        if not isinstance(value, self.type):
            raise TypeError("an {} is required".format(self.type.__name__))
        instance._dict_[self.name] = value._dict_
        instance.__dict__[self.name] = value

    def getter(self, instance):
        ret = instance.__dict__.get(self.name, sentinel)
        if ret is sentinel:
            ret = self.type.from_dict(instance._dict_[self.name])
            instance.__dict__[self.name] = ret
        return ret


class FieldList(Field):
    def __init__(self):
        super().__init__(maker=list)

    def setter(self, instance, value):
        raise AttributeError("FieldList cannot be set")


class FieldDict(Field):
    def __init__(self):
        super().__init__(maker=dict)

    def setter(self, instance, value):
        raise AttributeError("FieldList cannot be set")


class FieldCompList(Field):
    def __init__(self, factory):
        super().__init__(maker=list)
        self.factory = factory

    def setter(self, instance, value):
        raise AttributeError("FieldList cannot be set")


class FieldCompDict(Field):
    def __init__(self, factory):
        super().__init__(maker=dict)
        self.factory = factory

    def setter(self, instance, value):
        raise AttributeError("FieldList cannot be set")


class Namespace(OrderedDict):
    def __init__(self):
        super().__init__()
        self.fields = {}

    def __setitem__(self, key, val):
        super().__setitem__(key, val)
        if isinstance(val, Field):
            val.set_name(key)
            self.fields[key] = val

    def __delitem__(self, key):
        raise RuntimeError("Not allowed")


class ComponentMeta(type):
    @classmethod
    def __prepare__(cls, name, bases):
        return Namespace()

    def __init__(cls, name, bases, dct):
        type.__init__(cls, name, bases, dct)
        cls._fields_ = dct.fields
        cls._names_ = frozenset(dct.fields.keys())


class Component(metaclass=ComponentMeta):
    def __init__(self, **kwargs):
        names = self._names_
        delta = frozenset(kwargs) - names
        if delta:
            extra = ', '.join(sorted(delta))
            raise Error("Extra params: '{}'".format(extra))
        self._dict_ = kwargs
        missing = names - set(kwargs.keys())
        if not missing:
            return
        fields = self._fields_
        to_report = []
        klass = self.__class__
        for name in missing:
            field = fields[name]
            try:
                field.__get__(self, klass)
            except AttributeError:
                to_report.append(name)
        if to_report:
            missing = ', '.join(sorted(to_report))
            raise Error("Missing params: '{}'".format(missing))

    @classmethod
    def from_dict(cls, dct):
        self = object.__new__(cls)
        self._dict_ = dct
        return self

    def as_dict(self):
        return self._dict_
