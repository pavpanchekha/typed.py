import specialize

def mk_type(name, is_, sub_):
    class T(specialize.Type):
        def is_(self, x): return is_ (x)
        def sub(self, X): return sub_(X)
    return T(name)

def type_restrict(t, fn, name=None):
    A = mk_type(name if name is not None else "{type/restrict %s}" % t,
                lambda x: t.is_(x) and fn(x),
                lambda X: X.sup(t) or X == A)
    return A

def type_fn(fn, name=None):
    A = mk_type(name if name is not None else "{type/fn}",
                lambda x: fn(x),
                lambda X: X in (A, Object))
    return A

def type_eq(obj, name=None):
    A = mk_type(name if name is not None else "{type/= %s}" % obj,
                lambda x: x == obj,
                lambda X: X.is_(obj))

def type_python(t, name=None):
    A = type_fn(lambda x: isinstance(x, t),
                name if name is not None else "{type/type %s}" % t)
    return A

class typed_tuple(specialize.Type):
    def __init__(self, *args):
        specialize.Type.__init__(self, " * ".join(t.name for t in args))
        self.types = args

    def is_(self, x):
        return Tuple.is_(x) and len(x) == len(self.types) and all(T.is_(el) for el, T in zip(x, self.types))

    def sub(self, X):
        if isinstance(X, typed_tuple):
            return all(T.sub(S) for T, S in zip(self.types, X.types))
        else:
            return X.sup(Tuple)
specialize.Type.__mul__ = lambda *args: typed_tuple(*args)
specialize.Type.__pow__ = lambda type, n: typed_tuple(*([type] * n))

class typed_union(specialize.Type):
    def __init__(self, *args):
        specialize.Type.__init__(self, " | ".join(t.name for t in args))
        self.types = args

    def is_(self, x):
        return any(T.is_(x) for T in self.types)

    def sub(self, X):
        if X == self:
            return True
        else:
            return any(X.sup(T) for T in self.types)
specialize.Type.__or__ = lambda *args: typed_union(*args)

specialize.Type.__lt__ = lambda T, val: type_restrict(T, lambda x: x < val, "%s < %s" % (T.name, val))
specialize.Type.__le__ = lambda T, val: type_restrict(T, lambda x: x <= val, "%s <= %s" % (T.name, val))
specialize.Type.__gt__ = lambda T, val: type_restrict(T, lambda x: x > val, "%s < %s" % (val, T.name))
specialize.Type.__ge__ = lambda T, val: type_restrict(T, lambda x: x >= val, "%s <= %s" % (val, T.name))

class OneOf(specialize.Type):
    def __init__(self, *args):
        specialize.Type.__init__(self, "OneOf(%s)" % ", ".join(map(repr, args)))
        self.args = args

    def is_(self, x):
        return x in self.args

    def sub(self, X):
        if isinstance(X, OneOf):
            return all(i in X.args for i in self.args)
        else:
            return False

Object  = mk_type("Object", lambda x: True, lambda X: X == Object)
Complex = type_fn(lambda x: type(x) in map(type, [0, 0L, 0.0, 0j]), "Complex")
Real    = type_restrict(Complex, lambda x: not isinstance(x, complex), "Real")
Integer = type_restrict(Real, lambda x: not isinstance(x, float), "Integer")

Boolean = type_python(bool, "Boolean")
String  = type_python(str,  "String")
Type    = type_python(specialize.Type, "Type")
PyType  = type_python(type, "PyType")
Tuple   = type_python(tuple, "Tuple")

class List_(specialize.Type):
    """A covariant homogenous list type"""

    def __init__(self, T=Object):
        self.T = T
        if T == Object:
            self.name = "List"
        else:
            self.name = "List(%s)" % T.name

    def __call__(self, S):
        if self.T != Object:
            raise AttributeError("List object '%s' is not callable" % self.name)
        else:
            return List_(S)

    def is_(self, x):
        return isinstance(x, list) and all(self.T.is_(el) for el in x)

    def sub(self, X):
        if isinstance(X, List_):
            return X.T.sup(self.T)
        else:
            return X.sup(Object)
List = List_()

class Dict_(specialize.Type):
    """A covariant homogenous dict type"""

    def __init__(self, K=Object, V=Object):
        self.K = K
        self.V = V
        if K == Object:
            self.name = "Dict"
        elif V == Object:
            self.name = "Dict(%s)" % K.name
        else:
            self.name = "Dict(%s, %s)" % (K.name, V.name)

    def __call__(self, S, T=Object):
        if self.K != Object:
            raise AttributeError("Dict object '%s' is not callable" % self.name)
        else:
            return Dict_(S, T)

    def is_(self, x):
        return isinstance(x, dict) and all(self.K.is_(el) for el in x.keys()) and all(self.V.is_(el) for el in x.values())

    def sub(self, X):
        if isinstance(X, Dict):
            return X.K.sup(self.K) and X.V.sup(self.V)
        else:
            return X.sup(Object)
Dict = Dict_()

_isinstance = isinstance
_issubclass = issubclass
