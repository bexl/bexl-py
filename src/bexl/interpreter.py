import sys

from six import reraise

from .dispatcher import UNARY_OPERATORS, BINARY_OPERATORS, FUNCTIONS
from .errors import InterpreterError
from .resolver import VariableResolver
from .types import make_value, Types


def wrap_and_raise(node):
    exc = sys.exc_info()
    exc[1].node = node
    reraise(exc[0], exc[1], exc[2])


class Interpreter(object):
    """
    An interpreter for REXL. Interprets the output of a parser and returns the
    resulting value of the expression.
    """

    def interpret(self, tree, variable_resolver=None):
        """
        Interprets the AST and produces the resulting value

        :param tree: the parsed AST to interpret
        :type tree: bexl.nodes.Expression
        :param variable_resolver:
            the mechanism used to retrieve the Value for variables referenced
            in the expression
        :type variable_resolver: bexl.VariableResolver|dict
        :rtype: bexl.Value
        """

        resolver = VariableResolver.make_from(variable_resolver)
        return tree.accept(self, resolver=resolver)

    def visit_literal(self, node, resolver):  # noqa: no-self-use,unused-argument
        return make_value(node.data_type, node.value)

    def visit_grouping(self, node, resolver):
        return node.expression.accept(self, resolver=resolver)

    def visit_list(self, node, resolver):
        elements = [
            subnode.accept(self, resolver=resolver)
            for subnode in node.elements
        ]
        return make_value(Types.LIST, elements)

    def visit_variable(self, node, resolver):  # noqa: no-self-use
        try:
            return resolver(node.name)
        except InterpreterError:
            wrap_and_raise(node)

    def visit_property(self, node, resolver):
        expression = node.expression.accept(self, resolver=resolver)
        prop = make_value(Types.STRING, node.name)
        try:
            return FUNCTIONS.call('property', expression, prop)
        except InterpreterError:
            wrap_and_raise(node)

    def visit_indexing(self, node, resolver):
        expression = node.expression.accept(self, resolver=resolver)
        if node.index is not None:
            index = node.index.accept(self, resolver=resolver)
            try:
                return FUNCTIONS.call('at', expression, index)
            except InterpreterError:
                wrap_and_raise(node)

        else:
            start = end = None
            if node.start:
                start = node.start.accept(self, resolver=resolver)
            else:
                start = make_value(Types.INTEGER, 0)
            if node.end:
                end = node.end.accept(self, resolver=resolver)

            try:
                if end:
                    return FUNCTIONS.call('slice', expression, start, end)
                return FUNCTIONS.call('slice', expression, start)
            except InterpreterError:
                wrap_and_raise(node)

    def visit_unary(self, node, resolver):
        right = node.right.accept(self, resolver=resolver)

        try:
            return UNARY_OPERATORS.call(node.name, right)
        except InterpreterError:
            wrap_and_raise(node)

    def visit_binary(self, node, resolver):
        left = node.left.accept(self, resolver=resolver)
        right = node.right.accept(self, resolver=resolver)

        try:
            return BINARY_OPERATORS.call(
                node.name,
                left,
                right,
            )
        except InterpreterError:
            wrap_and_raise(node)

    def visit_function(self, node, resolver):
        arguments = [
            subnode.accept(self, resolver=resolver)
            for subnode in node.arguments
        ]

        try:
            return FUNCTIONS.call(node.name, *arguments)
        except InterpreterError:
            wrap_and_raise(node)

