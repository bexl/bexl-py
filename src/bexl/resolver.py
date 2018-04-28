from collections import Mapping, MutableMapping

from six import iteritems

from .errors import BexlError, ResolverError
from .types import python_to_bexl


class VariableResolver(MutableMapping):
    """
    A class/interface used by the BEXL Interpreter to resolve variable it finds
    in a BEXL expression to a value.
    """

    @classmethod
    def make_from(cls, value):
        """
        Turns the Mapping object into a VariableResolver that can be used by
        the BEXL Interpreter.

        :param value: the object to create a VariableResolver from
        :type value: Mapping
        :rtype: VariableResolver
        """

        if value is None:
            return cls()
        if isinstance(value, VariableResolver):
            return value
        if isinstance(value, Mapping):
            return cls(**value)
        raise BexlError(
            'Cannot create VariableResolver from: %r' % (value,)
        )

    def __init__(self, **kwargs):  # noqa: super-init-not-called
        self._variables = {}
        for key, value in iteritems(kwargs):
            self.__set(key, value)

    def __call__(self, name):
        """
        Retrieves the BEXL Value for the given variable name

        :param name: the name of the variable to resolve
        :type name: str
        :rtype: bexl.types.Value
        """

        if name not in self._variables:
            raise ResolverError(
                'Could not resolve variable "%s"' % (
                    name,
                ),
            )
        return self._variables[name]

    def __setitem__(self, key, value):
        self.__set(key, value)

    def __set(self, key, value):
        self._variables[key] = python_to_bexl(value)

    def __getitem__(self, key):
        return self._variables[key]

    def __delitem__(self, key):
        del self._variables[key]

    def __iter__(self):
        return iter(self._variables)

    def __len__(self):
        return len(self._variables)

