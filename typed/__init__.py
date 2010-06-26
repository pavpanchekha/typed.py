from .specialize import Type, typed, TypedError, typedef
from .types import Object, Real, Integer, Boolean, String, Type, PyType, Tuple, Complex, OneOf, List, Dict

from .types import type_restrict as restrict, type_fn as fn, type_eq as eq, type_python as from_pytype, _isinstance, _issubclass

@typed(Object, Type)
def isinstance(x, T):
    return T.is_(x)

@typed(Object, PyType)
def isinstance(x, T):
    return _isinstance(x, T)

@typed(Type, Type)
def issubclass(T, S):
    return T.sub(S)

@typed(PyType, PyType)
def issubclass(T, S):
    return _issubclass(T, S)

