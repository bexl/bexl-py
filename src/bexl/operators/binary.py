from ..dispatcher import BINARY_OPERATORS, FUNCTIONS
from ..token import TokenType
from ..types import Types


SPECS = (
    (
        TokenType.PLUS,
        (
            (Types.INTEGER, Types.INTEGER),
            (Types.FLOAT, Types.INTEGER),
            (Types.INTEGER, Types.FLOAT),
            (Types.FLOAT, Types.FLOAT),
            (Types.DATE, Types.INTEGER),
            (Types.DATE, Types.FLOAT),
            (Types.INTEGER, Types.DATE),
            (Types.FLOAT, Types.DATE),
            (Types.DATETIME, Types.INTEGER),
            (Types.DATETIME, Types.FLOAT),
            (Types.INTEGER, Types.DATETIME),
            (Types.FLOAT, Types.DATETIME),
            (Types.TIME, Types.INTEGER),
            (Types.TIME, Types.FLOAT),
            (Types.INTEGER, Types.TIME),
            (Types.FLOAT, Types.TIME),
        ),
        lambda left, right: FUNCTIONS.call('add', left, right),
    ),

    (
        TokenType.MINUS,
        (
            (Types.INTEGER, Types.INTEGER),
            (Types.FLOAT, Types.INTEGER),
            (Types.INTEGER, Types.FLOAT),
            (Types.FLOAT, Types.FLOAT),
            (Types.DATE, Types.INTEGER),
            (Types.DATE, Types.FLOAT),
            (Types.DATETIME, Types.INTEGER),
            (Types.DATETIME, Types.FLOAT),
            (Types.DATE, Types.DATE),
            (Types.DATE, Types.DATETIME),
            (Types.DATETIME, Types.DATE),
            (Types.DATETIME, Types.DATETIME),
            (Types.TIME, Types.INTEGER),
            (Types.TIME, Types.FLOAT),
            (Types.TIME, Types.TIME),
        ),
        lambda left, right: FUNCTIONS.call('subtract', left, right),
    ),

    (
        TokenType.STAR,
        (
            (Types.INTEGER, Types.INTEGER),
            (Types.FLOAT, Types.INTEGER),
            (Types.INTEGER, Types.FLOAT),
            (Types.FLOAT, Types.FLOAT),
        ),
        lambda left, right: FUNCTIONS.call('multiply', left, right),
    ),

    (
        TokenType.SLASH,
        (
            (Types.INTEGER, Types.INTEGER),
            (Types.FLOAT, Types.INTEGER),
            (Types.INTEGER, Types.FLOAT),
            (Types.FLOAT, Types.FLOAT),
        ),
        lambda left, right: FUNCTIONS.call('divide', left, right),
    ),

    (
        TokenType.PERCENT,
        (
            (Types.INTEGER, Types.INTEGER),
            (Types.FLOAT, Types.INTEGER),
            (Types.INTEGER, Types.FLOAT),
            (Types.FLOAT, Types.FLOAT),
        ),
        lambda left, right: FUNCTIONS.call('modulo', left, right),
    ),

    (
        TokenType.STAR_STAR,
        (
            (Types.INTEGER, Types.INTEGER),
            (Types.FLOAT, Types.INTEGER),
            (Types.INTEGER, Types.FLOAT),
            (Types.FLOAT, Types.FLOAT),
        ),
        lambda left, right: FUNCTIONS.call('pow', left, right),
    ),

    (
        TokenType.AMPERSAND,
        (),
        lambda left, right: FUNCTIONS.call('and', left, right),
    ),

    (
        TokenType.PIPE,
        (),
        lambda left, right: FUNCTIONS.call('or', left, right),
    ),

    (
        TokenType.CARET,
        (),
        lambda left, right: FUNCTIONS.call('xor', left, right),
    ),

    (
        TokenType.EQUAL_EQUAL,
        (),
        lambda left, right: FUNCTIONS.call('equal', left, right),
    ),

    (
        TokenType.BANG_EQUAL,
        (),
        lambda left, right: FUNCTIONS.call('notEqual', left, right),
    ),

    (
        TokenType.LESSER,
        (),
        lambda left, right: FUNCTIONS.call('lesser', left, right),
    ),

    (
        TokenType.LESSER_EQUAL,
        (),
        lambda left, right: FUNCTIONS.call('lesserEqual', left, right),
    ),

    (
        TokenType.GREATER,
        (),
        lambda left, right: FUNCTIONS.call('greater', left, right),
    ),

    (
        TokenType.GREATER_EQUAL,
        (),
        lambda left, right: FUNCTIONS.call('greaterEqual', left, right),
    ),
)


for operator, types, impl in SPECS:
    BINARY_OPERATORS.register(operator, *types)(impl)

