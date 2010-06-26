Multiple Dispatch and Inquisitive Types for Python
==================================================

``typed.py`` implements multimethods (also known as multiple dispatch) for
Python. However, instead of basing the types used for dispatch on the
standard Python class system, ``typed.py`` uses a method called `inquisitive
types`.

Diving In
---------

Start off by importing the ``typed`` module; you don't need anything besides
that. ::

    from typed import *

Some of the names in the typed module may conflict with names you yourself use:
``typed``, ``typedef``, ``restrict``, ``fn``, ``from_pytype``, and ``eq``. If
so, take special care to eliminate shadowing.

Now then, let's write a function::

    @typed(String, String)
    def combine(a, b):
        return a + b

This function will require both arguments to be strings::

    >>> combine("adsf", "adsf")
    'asdfasdf'
    >>> combine(1, 2)
    Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "typed/specialize.py", line 108, in __call__
        return self.match(args)[1](*args)
    File "typed/specialize.py", line 103, in match
        raise TypedError("No matches", self, [x[0] for x in self.sigs])
    typed.specialize.TypedError: No matches for function <typed function combine at 0xb733a4ec>. Alternatives:
            (<Type String>, <Type String>)

Scary looking error, huh? Note that it tells you the alternative signatures.

Anyway, let's define another variant to this function::

    @typed(String, Integer)
    def combine(a, n):
        return a + str(n)

And, we can use it normally::

    >>> combine("asdf", 12)
    'asdf12'
    >>> combine("asdf", "asdf")
    'asdfasdf'

Yay, both signatures work!

The builtin types include:

    - ``Object`` (anything at all, not just things that inherit from
      ``object``)
    - ``Complex`` (``complex``, ``float``, or and integral type)
    - ``Real`` (``float`` or an integral type)
    - ``Integer`` (``int`` or ``long``; an integral type)
    - ``Boolean`` (``bool``)
    - ``String`` (guess!)
    - ``Type`` (An inquisitive type)
    - ``PyType`` (A python class or type)
    - ``Tuple`` (A tuple of any length or type)
    - ``List`` (A list of any type) and ``List(T)`` (A list of type ``T``
      elements)
    - ``Dict`` (A dict of any type to any type), ``Dict(T)`` (A list where all
      keys have type ``T``), and ``Dict(K, V)`` (A dict with keys of type ``K``
      and values of type ``V``)
    - ``OneOf(*x)`` (Type of things equal to one of the elements of ``x``)

What are Inquisitive Types?
---------------------------

An inquisitive type is defined by two properties: `is` and `sub`. I'll skip the
second for now, but `is` (which in Python is the method ``is_`` of a type) just
takes an object and tells you if that object is an instance of the given type.
For example, the `is` method for ``Object`` is simply::

    def is(self, x):
        return True

Because, after all, everything is an object. Not that `a priori`, objects have
no type; one can only ask a type if an object is an instance. This is why they
are called `inquisitive`: you always have to ask if you want to know if an object
is an instance of something.

Now, what about that `sub` method I mentioned? This is the analog of
``issubclass`` for inquisitive types: it takes another type, and tells you if
the given type is a subclass of it. For example, the one for ``Object`` is::

    def sub(self, X):
        if X == self:
            return True
        else:
            return False

These subclass relations are used to determine which method to call if a
function has, for example, two implementations with signatures ``Integer,
Integer`` and ``Real, Real``: clearly you want the one with ``Integer``\ s to
be called if possible; and it is, because ``Integer.sub(Real)`` returns
``True``.

Now, the nice thing is that this allows you to construct more complex types
easily, using `type functions`. Don't worry, the concept is easy: it's a
function that takes a type and returns a type. For example, consider the
function ``restrict``. ``restrict(T, f, name)`` takes a type ``T`` and returns
a type that only says things are instances if they are instances of that type,
*and* satisfy the function ``f``. The ``name`` just names the resulting type.
So, for example::

    >>> EvenInt = restrict(Integer, lambda x: x % 2 == 0, "EvenInt")
    <type EvenInt>
    >>> isinstance(4, EvenInt)
    True
    >>> isinstance(3, EvenInt)
    False

Some other type functions are built in to ``typed.py``. ``fn(f)`` is another way
of saying ``restrict(Object, f)``. ``typedef(T, name)`` copies the type ``T``
and renames it (sometimes useful if you use type functions to construct types).
``eq(x)`` creates a new type whose only instance is ``x``; it's equivalent to
``OneOf(x)``. Finally, ``from_pytype`` is a compatibility feature, taking any
Python type and returning a new inquisitive type.

Furthermore, a few useful type functions have nice operator syntax. For example::

    >>> isinstance((3, 4), Integer * Integer)
    True
    >>> isinstance(("foo", "bar", "baz"), String ** 3)
    True
    >>> isinstance(5, Integer < 3)
    False
    >>> isinstance(7, Integer > -2)
    True
    >>> isinstance("a", eq("a") | eq("b"))
    True
    >>> map(lambda x: isinstance(x, Integer | String), [1, "a", 17.3, "17.3", True])
    [True, True, False, True, False]
    >>> isinstance(12, (3 < Integer) < 17)
    True

Note that in the last example, you *must* place parentheses around one of the
two comparisons. It doesn't matter which one; this is simply a fault of Python's
syntax.

Use in APIs
-----------

One can use ``typed.py`` for simple type checking::

    @typed(Real)
    def sqrt(x):
        ...

Or, you can use it to dispatch based on type::

    @typed(Real)
    def sqrt(x):
        import math
        return math.sqrt(x)

    @typed(Complex)
    def sqrt(x):
        import cmath
        return cmath.sqrt(x)

You can eliminate boring conditional checks::

    @typed(Integer < 10000)
    def is_prime(x):
        return do_bruteforce(x)

    @typed(Integer)
    def is_prime(x):
        return elliptic_curve_primality_test(x)

You can also dispatch, because these are inquisitive types, on specifics of the
arguments::

    @typed(restrict(String, lambda x: x.startswith("http")))
    def download(x):
        import urllib
        return urllib.urlopen(x).read()

    @typed(restrict(String, lambda x: x.startswith("ftp")))
    def download(x):
        import ftplib
        f = ftplib.FTP(dir)
        return f.getwelcome()

Finally, you can combine these to make those strings you ask people to pass to
identify things to do type-safe::

    Color = typedef(OneOf("green", "yellow", "red"), "Color")

    @typed(Banana, Color)
    def eat(b, color):
        if color == "green":
            print "Hold on"
        elif color == "yellow":
            print "Go ahead"
        elif color == "red":
            print "Where the **** did you get that banana?" # -- Mitch Hedburg

Admittedly, in that last example, you'd probably write three methods and use
``eq`` to create types corresponding to each color.

Lastly, you can now create singletons that are easy to use: just use ``eq``
constructors on a string.

Type Types and so on
--------------------

::

    >>> isinstance(Integer, Type)
    True

See, types can have types (it's like metatypes, only it makes sense!). In fact,
it actually gets a bit spookier, because::

    >>> isinstance(Type, Type)
    True

It's ``Type``\ s all the way down! ::

    >>> isinstance(Object, Object)
    True

Until you hit the ``Object``\ s, that is.

A Short Note on Covariance
--------------------------

::

    >>> a = [1, 2, 3]
    >>> isinstance(a, List(Integer))
    True
    >>> isinstance(a, List(Complex))
    True
    >>> a[1] = "asdf"
    >>> isinstance(a, List(Integer))
    False

``List``\ s (and ``Dict``\ ionaries) covary with their contained types. This
raises the usual endless troubles. Cry me a river. Or, better yet, deal with it.

