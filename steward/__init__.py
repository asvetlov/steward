from collections import OrderedDict, MutableMapping


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
            ret, as_dct = self.getter(instance._dict_)
            instance.__dict__[self.name] = ret
            instance._dict_[self.name] = as_dct
        return ret

    def getter(self, dct):
        ret = dct.get(self.name, sentinel)
        if ret is sentinel and self.default is not sentinel:
            ret = self.default
        elif ret is sentinel:
            raise AttributeError("'{.name}' is not initialized".format(self))
        return ret, ret

    def __set__(self, instance, value):
        assert self.name
        ret, as_dct = self.setter(value)
        instance.__dict__[self.name] = ret
        instance._dict_[self.name] = as_dct

    def setter(self, value):
        return value, value


class FieldComp(Field):
    def __init__(self, type, *, default=sentinel):
        if default is not None and default is not sentinel:
            if not isinstance(default, type):
                raise TypeError("an {} is required".format(self.type.__name__))
        super().__init__(default=default)
        self.type = type

    def setter(self, value):
        if value is None:
            return None, None
        if not isinstance(value, self.type):
            raise TypeError("an {} is required".format(self.type.__name__))
        return value, value._dict_

    def getter(self, dct):
        ret = dct.get(self.name, sentinel)
        if ret is sentinel and self.default is not sentinel:
            if self.default is None:
                return None, None
            else:
                return self.default, self.default._dict_
        elif ret is sentinel:
            raise AttributeError("'{.name}' is not initialized".format(self))
        else:
            return self.type.from_dict(ret) if ret is not None else None, ret


#class FieldList(Field):
#    def __init__(self, factory):
#        super().__init__(maker=list)
#        self.factory = factory
#
#    def setter(self, instance, value):
#        raise AttributeError("FieldList cannot be set")


class DictProxy(MutableMapping):
    @classmethod
    def _from_dict(cls, type, dct):
        ret = cls(type)
        ret._dict_ = dct
        return ret

    def __init__(self, type):
        self.type = type
        self._dict_ = {}
        self.__objects = {}

    def as_dict(self):
        return self._dict_

    def __len__(self):
        return len(self._dict_)

    def __iter__(self):
        return iter(self._dict_)

    def __getitem__(self, key):
        ret = self.__objects.get(key, sentinel)
        if ret is not sentinel:
            return ret
        subdict = self._dict_[key]
        assert isinstance(subdict, dict)
        ret = self.type.from_dict(subdict)
        self.__objects[key] = ret
        return ret

    def __setitem__(self, key, val):
        assert isinstance(val, self.type)
        self.__objects[key] = val
        self._dict_[key] = val._dict_

    def __delitem__(self, key):
        del self._dict_[key]
        self.__objects.pop(key, None)


class FieldDict(Field):
    def __init__(self, type):
        super().__init__()
        self.type = type

    def setter(self, value):
        raise AttributeError("FieldDict cannot be set")

    def getter(self, dct):
        val = dct.get(self.name, {})
        assert isinstance(dct, dict)
        return DictProxy._from_dict(self.type, val), val


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
        self._dict_ = {}
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
    def from_dict(cls, dct):
        self = object.__new__(cls)
        self._dict_ = dct
        return self

    def as_dict(self):
        return self._dict_
