Steward
=======

Library for easy bi-direction converting between plain JSON-like data
(numbers, strings, lists and dicts) and compound user-defined classes.


Let's look on simple example::

    >>> from steward import *
    >>> class Comp(Component):
    ...     a = Field()
    ...     b = Field(default=1)
    ...
    >>> v = Comp()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "steward/__init__.py", line 267, in __init__
        raise Error("Missing params: '{}'".format(missing))
    steward.Error: Missing params: 'a'
    >>> v = Comp(a=0)
    >>> dct = v.as_plain()
    >>> dct
    {'a': 0, 'b': 1}
    >>> v2 = Comp.from_plain(dct)
    >>> v2.a
    0
    >>> v2.b
    1
    >>> v2.as_plain()
    {'a': 0, 'b': 1}
