from ..dispatcher import FUNCTIONS
from ..errors import ExecutionError
from ..types import Types, make_value, cast


@FUNCTIONS.register(
    'not',
    (Types.BOOLEAN,),
)
def logical_not(value):
    return make_value(Types.BOOLEAN, not value.value)


@FUNCTIONS.register(
    'and',
)
def logical_and(left, right):
    left = cast(left, Types.BOOLEAN)
    right = cast(right, Types.BOOLEAN)
    return make_value(Types.BOOLEAN, left.value and right.value)


@FUNCTIONS.register(
    'or',
)
def logical_or(left, right):
    left = cast(left, Types.BOOLEAN)
    right = cast(right, Types.BOOLEAN)
    return make_value(Types.BOOLEAN, left.value or right.value)


@FUNCTIONS.register(
    'xor',
)
def logical_xor(left, right):
    left = cast(left, Types.BOOLEAN)
    right = cast(right, Types.BOOLEAN)
    return make_value(Types.BOOLEAN, left.value != right.value)


@FUNCTIONS.register(
    'if',
)
def if_func(*args):
    if len(args) < 3 or len(args) % 2 != 1:
        raise ExecutionError(
            'Incorrect number of arguments'
        )

    for i in range(0, len(args) - 1, 2):
        predicate = cast(args[i], Types.BOOLEAN)
        if predicate.raw_value:
            return args[i + 1]

    return args[-1]


@FUNCTIONS.register(
    'switch',
)
def switch(*args):
    if len(args) < 4 or len(args) % 2 != 0:
        raise ExecutionError(
            'Incorrect number of arguments'
        )

    value = args[0]

    for i in range(1, len(args) - 1, 2):
        result = FUNCTIONS.call('equal', value, args[i])
        if result.raw_value:
            return args[i + 1]

    return args[-1]

