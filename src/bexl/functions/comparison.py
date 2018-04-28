from ..dispatcher import FUNCTIONS
from ..types import Types, make_value, cast, TRUE, FALSE


def comparison(comparator, left, right):
    if left.data_type != right.data_type:
        right = cast(right, left.data_type)
    return make_value(
        Types.BOOLEAN,
        getattr(left, comparator)(right),
    )


@FUNCTIONS.register(
    'equal',
)
def equal(left, right):
    return comparison('__eq__', left, right)


@FUNCTIONS.register(
    'notEqual',
)
def not_equal(left, right):
    return comparison('__ne__', left, right)


@FUNCTIONS.register(
    'greater',
)
def greater(left, right):
    return comparison('__gt__', left, right)


@FUNCTIONS.register(
    'greaterEqual',
)
def greater_equal(left, right):
    return comparison('__ge__', left, right)


@FUNCTIONS.register(
    'lesser',
)
def lesser(left, right):
    return comparison('__lt__', left, right)


@FUNCTIONS.register(
    'lesserEqual',
)
def lesser_equal(left, right):
    return comparison('__le__', left, right)


@FUNCTIONS.register(
    'between',
    (Types.INTEGER, Types.INTEGER, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT, Types.INTEGER),
    (Types.INTEGER, Types.INTEGER, Types.FLOAT),
    (Types.INTEGER, Types.FLOAT, Types.FLOAT),
    (Types.FLOAT, Types.INTEGER, Types.INTEGER),
    (Types.FLOAT, Types.FLOAT, Types.INTEGER),
    (Types.FLOAT, Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.FLOAT, Types.FLOAT),
)
def between(value, start, end):
    if value.is_null or start.is_null or end.is_null:
        return FALSE

    start = cast(start, value.data_type)
    end = cast(end, value.data_type)

    if start <= value <= end:
        return TRUE
    return FALSE

