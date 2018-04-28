import inspect

from .errors import DispatchError


class Dispatcher(object):
    def __init__(self):
        self._functions = {}

    def register(self, name, *signatures):
        def wrapper(func):
            if name not in self._functions:
                self._functions[name] = {}
            if signatures:
                for signature in signatures:
                    self._functions[name][signature] = func
            else:
                self._functions[name] = func
            return func
        return wrapper

    def call(self, name, *args):
        if name not in self._functions:
            raise DispatchError(
                'No implementation exists for "%s"' % (name,)
            )

        func = self._functions[name]
        arg_types = tuple([
            arg.data_type
            for arg in args
        ])

        if arg_types:
            error = DispatchError(
                '"%s" cannot be invoked on arguments of type: %s' % (
                    name,
                    ', '.join(arg_types),
                ),
            )
        else:
            error = DispatchError(
                '"%s" cannot be invoked without arguments' % (
                    name,
                )
            )

        if isinstance(func, dict):
            func = func.get(arg_types)
            if not func:
                raise error

        else:
            argspec = inspect.getargspec(func)
            num_reqd_args = len(argspec.args) - len(argspec.defaults or [])
            if len(arg_types) < num_reqd_args:
                raise error

            elif len(arg_types) > len(argspec.args) and not argspec.varargs:
                raise error

        return func(*args)


class Registry(object):
    def __init__(self):
        self._dispatchers = {}

    def __call__(self, name):
        if name not in self._dispatchers:
            self._dispatchers[name] = Dispatcher()
        return self._dispatchers[name]


get_dispatcher = Registry()  # noqa: invalid-name


UNARY_OPERATORS = get_dispatcher('unary_operators')
BINARY_OPERATORS = get_dispatcher('binary_operators')
FUNCTIONS = get_dispatcher('functions')

