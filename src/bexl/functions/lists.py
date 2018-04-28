import datetime

from ..dispatcher import FUNCTIONS, DispatchError
from ..types import Types, make_value, NULL, TRUE, FALSE, cast, \
    is_consistently_typed


def dtkey(val):
    if isinstance(val.raw_value, datetime.date) \
            and not isinstance(val.raw_value, datetime.datetime):
        return datetime.datetime.combine(val.raw_value, datetime.time(0, 0, 0))
    return val.raw_value


@FUNCTIONS.register(
    'min',
    (Types.LIST,)
)
def min_list(values):
    if values.is_null:
        return NULL

    all_numbers = is_consistently_typed(
        values.raw_value,
        (Types.INTEGER, Types.FLOAT),
    )
    all_dates = is_consistently_typed(
        values.raw_value,
        (Types.DATE, Types.DATETIME),
    )
    all_times = is_consistently_typed(values.raw_value, (Types.TIME,))
    if not all_numbers and not all_dates and not all_times:
        raise DispatchError(
            '"min" must be invoked on a list that contains all INTEGER/FLOAT,'
            ' all DATE/DATETIME, or all TIME values'
        )

    vals = [
        val
        for val in values.raw_value
        if not val.is_null
    ]
    if not vals:
        return NULL

    reduced = min(vals, key=dtkey)
    return reduced


@FUNCTIONS.register(
    'max',
    (Types.LIST,)
)
def max_list(values):
    if values.is_null:
        return NULL

    all_numbers = is_consistently_typed(
        values.raw_value,
        (Types.INTEGER, Types.FLOAT),
    )
    all_dates = is_consistently_typed(
        values.raw_value,
        (Types.DATE, Types.DATETIME),
    )
    all_times = is_consistently_typed(values.raw_value, (Types.TIME,))
    if not all_numbers and not all_dates and not all_times:
        raise DispatchError(
            '"max" must be invoked on a list that contains all INTEGER/FLOAT,'
            ' all DATE/DATETIME, or all TIME values'
        )

    vals = [
        val
        for val in values.raw_value
        if not val.is_null
    ]
    if not vals:
        return NULL

    reduced = max(vals, key=dtkey)
    return reduced


@FUNCTIONS.register(
    'sum',
    (Types.LIST,)
)
def sum_list(values):
    if values.is_null:
        return NULL

    if not is_consistently_typed(
            values.raw_value,
            (Types.INTEGER, Types.FLOAT)):
        raise DispatchError(
            '"sum" cannot be invoked on a list containing values of types'
            ' other than INTEGER or FLOAT'
        )

    vals = [
        val
        for val in values.raw_value
        if not val.is_null
    ]

    result = sum([val.raw_value for val in vals])

    return make_value(
        Types.FLOAT if isinstance(result, float) else Types.INTEGER,
        result,
    )


@FUNCTIONS.register(
    'average',
    (Types.LIST,)
)
def average_list(values):
    if values.is_null:
        return NULL

    if not is_consistently_typed(
            values.raw_value,
            (Types.INTEGER, Types.FLOAT)):
        raise DispatchError(
            '"average" cannot be invoked on a list containing values of types'
            ' other than INTEGER or FLOAT'
        )

    vals = [
        val
        for val in values.raw_value
        if not val.is_null
    ]
    if not vals:
        return NULL

    result = float(sum([val.raw_value for val in vals])) / len(vals)

    return make_value(Types.FLOAT, result)


@FUNCTIONS.register(
    'all',
    (Types.LIST,)
)
def all_list(values):
    if values.is_empty:
        return TRUE

    vals = [
        cast(val, Types.BOOLEAN).raw_value
        for val in values.raw_value
    ]

    return TRUE if all(vals) else FALSE


@FUNCTIONS.register(
    'any',
    (Types.LIST,)
)
def any_list(values):
    if values.is_empty:
        return FALSE

    vals = [
        cast(val, Types.BOOLEAN).raw_value
        for val in values.raw_value
    ]

    return TRUE if any(vals) else FALSE


@FUNCTIONS.register(
    'none',
    (Types.LIST,)
)
def none_list(values):
    if values.is_empty:
        return TRUE

    vals = [
        cast(val, Types.BOOLEAN).raw_value
        for val in values.raw_value
    ]

    return FALSE if any(vals) else TRUE


@FUNCTIONS.register(
    'count',
    (Types.LIST,)
)
def count_list(values):
    if values.is_empty:
        cnt = 0
    else:
        cnt = len([
            val
            for val in values.raw_value
            if cast(val, Types.BOOLEAN).raw_value
        ])

    return make_value(Types.INTEGER, cnt)

