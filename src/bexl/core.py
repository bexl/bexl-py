from .interpreter import Interpreter
from .parser import Parser
from .lexer import Lexer
from .types import bexl_to_python


def evaluate(
        source,
        variable_resolver=None,
        native=True,
        lexer=Lexer,
        parser=Parser):
    """
    Evaluates the given BEXL expression and returns its result.

    :param source: the BEXL expression to evaluate
    :type source: str
    :param variable_resolver:
        the mechanism used to retrieve the Value for variables referenced
        in the expression
    :type variable_resolver: bexl.VariableResolver|dict
    :param native:
        whether or not this function should return the raw bexl.Value returned
        by the BEXL interpreter, or the native Python value. If not specified,
        the native Python value is returned.
    :type native: bool
    :param lexer:
        the Lexer to use when parsing the expression. If not specified,
        defaults to bexl.Lexer.
    :type lexer: bexl.Lexer
    :param parser:
        the Parser to use when parsing the expression. If not specified,
        defaults to bexl.Parser.
    :type parser: bexl.Parser
    """

    tree = parser(lexer=lexer).parse(source)

    result = Interpreter().interpret(tree, variable_resolver=variable_resolver)

    if native:
        return bexl_to_python(result)
    return result

