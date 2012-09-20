__version__ = '0.0.2'

from collections import OrderedDict, MutableMapping, MutableSequence, Sequence


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
        name = self.name
        assert name
        ret = instance.__dict__.get(name, sentinel)
        if ret is sentinel:
            ret, plainval = self.getter(instance._plain_.get(name, sentinel))
            instance.__dict__[name] = ret
            instance._plain_[name] = plainval
        return ret

    def getter(self, plainval):
        ret = plainval
        if ret is sentinel and self.default is not sentinel:
            ret = self.default
        elif ret is sentinel:
            raise AttributeError("'{.name}' is not initialized".format(self))
        return ret, ret

    def __set__(self, instance, value):
        name = self.name
        assert name
        ret, plainval = self.setter(value)
        instance.__dict__[name] = ret
        instance._plain_[name] = plainval

    def setter(self, value):
        return value, value


class FieldComp(Field):
    def __init__(self, type, *, default=sentinel):
        if default is not None and default is not sentinel:
            if not isinstance(default, type):
                raise TypeError("an {} is required, got {}".format(
                        self.type.__name__, type(default).__name__))
        super().__init__(default=default)
        self.type = type

    def setter(self, value):
        if value is None:
            return None, None
        if not isinstance(value, self.type):
            raise TypeError("an {} is required, got {}".format(
                    self.type.__name__, type(value).__name__))
        return value, value._plain_

    def getter(self, plainval):
        ret = plainval
        if ret is sentinel and self.default is not sentinel:
            if self.default is None:
                return None, None
            else:
                return self.default, self.default._plain_
        elif ret is sentinel:
            raise AttributeError("'{.name}' is not initialized".format(self))
        else:
            return self.type.from_plain(ret) if ret is not None else None, ret


class DictProxy(MutableMapping):
    @classmethod
    def _from_plain(cls, type, plainval):
        ret = cls(type)
        ret._plain_ = plainval
        return ret

    def __init__(self, type):
        self.type = type
        self._plain_ = {}
        self.__objects = {}

    def as_plain(self):
        return self._plain_

    def __len__(self):
        return len(self._plain_)

    def __iter__(self):
        return iter(self._plain_)

    def __getitem__(self, key):
        ret = self.__objects.get(key, sentinel)
        if ret is not sentinel:
            return ret
        plainitem = self._plain_[key]
        assert isinstance(plainitem, dict)
        ret = self.type.from_plain(plainitem)
        self.__objects[key] = ret
        return ret

    def __setitem__(self, key, val):
        assert isinstance(val, self.type)
        self.__objects[key] = val
        self._plain_[key] = val._plain_

    def __delitem__(self, key):
        del self._plain_[key]
        self.__objects.pop(key, None)


class FieldDict(Field):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def setter(self, value):
        raise AttributeError("FieldDict cannot be set")

    def getter(self, plainval):
        if plainval is sentinel:
            plainval = {}
        assert isinstance(plainval, dict)
        return DictProxy._from_plain(self.type, plainval), plainval


class ListProxy(MutableSequence):
    @classmethod
    def _from_plain(cls, type, plainval):
        ret = cls(type)
        ret._plain_ = plainval
        return ret

    def __init__(self, type):
        self.type = type
        self._plain_ = []
        self.__shadow = None

    def as_plain(self):
        return self._plain_

    def __len__(self):
        return len(self._plain_)

    def __iter__(self):
        if self.__shadow is None:
            t = self.type
            self.__shadow = [t.from_plain(i) for i in self._plain_]
        return iter(self.__shadow)

    def __getitem__(self, index):
        if self.__shadow is None:
            t = self.type
            self.__shadow = [t.from_plain(i) for i in self._plain_]
        return self.__shadow[index]

    def __setitem__(self, index, val):
        if self.__shadow is None:
            t = self.type
            self.__shadow = [t.from_plain(i) for i in self._plain_]
        self.__shadow[index] = val
        if isinstance(val, Sequence):
            nv = []
            for i in val:
                assert isinstace(i, self.type)
                nv.append(i._plain_)
        else:
            nv = val._plain_
        self._plain_[index] = nv

    def __delitem__(self, index):
        if self.__shadow is None:
            t = self.type
            self.__shadow = [t.from_plain(i) for i in self._plain_]
        del self._plain_[index]
        del self.__shadow[index]

    def insert(self, index, value):
        assert isinstance(value, self.type)
        if self.__shadow is None:
            t = self.type
            self.__shadow = [t.from_plain(i) for i in self._plain_]
        self.__shadow.insert(index, value)
        self._plain_.insert(index, value._plain_)


class FieldList(Field):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def setter(self, value):
        raise AttributeError("FieldList cannot be set")

    def getter(self, plainval):
        if plainval is sentinel:
            plainval = []
        if isinstance(plainval, tuple):
            plainval = list(plainval)
        assert isinstance(plainval, list), plainval
        return ListProxy._from_plain(self.type, plainval), plainval


class Namespace(OrderedDict):
    def __init__(self, bases):
        super().__init__()
        self.fields = {}
        for b in bases:
            if issubclass(b, Component):
                self.fields.update(b._fields_)

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
        return Namespace(bases)

    def __init__(cls, name, bases, dct):
        type.__init__(cls, name, bases, dct)
        cls._fields_ = dct.fields
        cls._names_ = frozenset(dct.fields.keys())


class Component(metaclass=ComponentMeta):

    def __init__(self, **kwargs):
        self._plain_ = {}
        names = self._names_
        delta = frozenset(kwargs) - names
        if delta:
            extra = ', '.join(sorted(delta))
            raise Error("Extra params: '{}'".format(extra))
        missing = []
        fields = self._fields_
        for k, v in kwargs.items():
            if k in names:
                fields[k].__set__(self, v)
        missing = names - set(kwargs.keys())
        if not missing:
            return
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
    def from_plain(cls, plainval):
        self = object.__new__(cls)
        self._plain_ = plainval
        return self

    def as_plain(self):
        return self._plain_
