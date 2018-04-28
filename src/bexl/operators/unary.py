from ..dispatcher import UNARY_OPERATORS, FUNCTIONS
from ..token import TokenType
from ..types import Types


@UNARY_OPERATORS.register(
    TokenType.MINUS,
    (Types.INTEGER,),
    (Types.FLOAT,),
)
def negative(value):
    return FUNCTIONS.call('negative', value)


@UNARY_OPERATORS.register(
    TokenType.BANG,
    (Types.BOOLEAN,),
)
def logical_not(value):
    return FUNCTIONS.call('not', value)

