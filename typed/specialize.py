import warnings
DEBUG = False

def debug_print(*args):
    if DEBUG: print "~>", " ".join(map(str, args))
    return args[-1]

class TypedError(TypeError):
    def __init__(self, text, fn, sigs):
        self.text = text
        self.fn   = fn
        self.sigs = sigs

    def __str__(self):
        s = ["%s for function %s.%s" % (self.text, self.fn, " Alternatives:" if len(self.sigs) else "")]
        for sig in self.sigs:
            s.append(str(sig))
        return "\n\t".join(s)

class TypedWarning(UserWarning): pass

class Type(object):
    def __init__(self, name): self.name = name
    def __hash__(self): return hash(self.name)
    def __repr__(self): return "<Type %s>" % self.name

    def is_(self, x): raise NotImplementedError
    def sub(self, X): raise NotImplementedError
    def sup(self, X): return X.sub(self)


def is_specialization(fn1, fn2):
    return all(t1.sub(t2) for t1, t2 in zip(fn1, fn2))

def is_generalization(fn1, fn2): return is_specialization(fn2, fn1)

def matches(args, fn1):
    return len(args) == len(fn1) and all(t.is_(arg) for t, arg in zip(fn1, args))

class FnStore(object):
    registry = {}

    def __init__(self, *sigs, **kwargs):
        self.sigs = dict((sig, []) for sig in sigs)
        self.toposort()
        self.__name__ = kwargs.get("name", "<lambda>")
        if self.__name__ != "<lambda>" and self.__name__ not in FnStore.registry:
            FnStore.registry[self.__name__] = self

    def toposort(self):
        for node in self.sigs:
            for other_node in self.sigs:
                if node[0] == other_node[0]: continue
                if is_generalization(node[0], other_node[0]):
                    self.sigs[node].append(other_node)

    def add(self, node): # TODO: is currently stupidly slow
        if node[0] in [sig for sig, fn in self.sigs]:
            warnings.warn(TypedWarning("Overwriting signature %s in %s" % (sig, self)))
            del self.sigs[(sig, fn)]
        self.sigs = dict((sig, []) for sig in self.sigs)
        self.sigs[node] = []
        self.toposort()

    def match(self, args):
        nodedict = dict.copy(self.sigs)

        def rec_remove(node, depth=1):
            debug_print("  " * depth + "Removing:", node)
            for i in nodedict[node]:
                if i in nodedict:
                    rec_remove(nodedict[node][0], depth + 1)
            del nodedict[node]

        flag = True
        while flag:
            flag = False
            for sig in nodedict:
                if not matches(args, sig[0]):
                    flag = True
                    break
            if flag:
                debug_print("Asking to remove:", sig[0])
                rec_remove(sig)

        # At this point, all things are valid, so we need only the bottom
        # ones

        flag = True
        while flag:
            flag = False
            for sig in nodedict.keys():
                for other_sig in nodedict[sig]:
                    if other_sig in nodedict:
                        debug_print(sig[0], "is shadowed by", other_sig[0])
                        del nodedict[sig]
                        flag = True
                        break

        if len(nodedict) > 1:
            raise TypedError("More than one match", self, [x[0] for x in nodedict])
        elif len(nodedict) == 0:
            raise TypedError("No matches", self, [x[0] for x in self.sigs])

        return nodedict.keys()[0]

    def __call__(self, *args):
        return self.match(args)[1](*args)

    def __repr__(self):
        return "<typed function %s at 0x%x>" % (self.__name__, id(self))

    def __str__(self):
        return repr(self)

    def __del__(self):
        if FnStore is None:
            return
        if self.__name__ != "<lambda>" and self.__name__ in FnStore.registry:
            del FnStore.registry[self.__name__]

def typed(*args, **kwargs):
    def decorator(f):
        name = kwargs.get("name", f.__name__)
        s = FnStore.registry.get(name, FnStore(name=name))
        s.add((args, f))
        return s
    return decorator

def typedef(T, name):
    import copy
    S = copy.deepcopy(T)
    S.name = name
    return S

def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
