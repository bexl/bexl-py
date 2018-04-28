import six

from ..dispatcher import FUNCTIONS
from ..errors import DispatchError, ExecutionError
from ..types import Types, make_value, TRUE, FALSE, NULL


@FUNCTIONS.register(
    'in',
)
def value_in(needle, haystack):
    if haystack.data_type == Types.LIST:
        if haystack.is_null:
            return FALSE

        return TRUE if needle.value in haystack.value else FALSE

    elif needle.data_type == Types.STRING \
            and haystack.data_type == Types.STRING:
        if needle.is_null or haystack.is_null:
            return FALSE

        return TRUE if needle.value in haystack.value else FALSE

    else:
        raise DispatchError(
            '"in" cannot be invoked on arguments of type: %s' % (
                ', '.join([needle.data_type, haystack.data_type]),
            ),
        )


@FUNCTIONS.register(
    'length',
    (Types.STRING,),
    (Types.LIST,),
)
def seq_length(value):
    if value.is_empty:
        vlen = 0
    else:
        vlen = len(value.raw_value)
    return make_value(Types.INTEGER, int(vlen))


@FUNCTIONS.register(
    'head',
    (Types.STRING,),
    (Types.STRING, Types.INTEGER),
    (Types.STRING, Types.FLOAT),
    (Types.LIST,),
    (Types.LIST, Types.INTEGER),
    (Types.LIST, Types.FLOAT),
)
def head(value, length=None):
    if value.is_null:
        return make_value(value.data_type, None)

    if length is None or length.is_null:
        length = 1
    else:
        length = int(length.raw_value)

    return make_value(value.data_type, value.raw_value[:length])


@FUNCTIONS.register(
    'tail',
    (Types.STRING,),
    (Types.STRING, Types.INTEGER),
    (Types.STRING, Types.FLOAT),
    (Types.LIST,),
    (Types.LIST, Types.INTEGER),
    (Types.LIST, Types.FLOAT),
)
def tail(value, length=None):
    if value.is_null:
        return make_value(value.data_type, None)

    if length is None or length.is_null:
        length = 1
    else:
        length = int(length.raw_value)

    return make_value(value.data_type, value.raw_value[-1 * length:])


@FUNCTIONS.register(
    'concat',
)
def concat(value, *values):
    values = [value] + list(values)
    arg_types = [val.data_type for val in values]  # noqa: no-member
    mismatched = [atype for atype in arg_types if atype != arg_types[0]]
    if arg_types[0] not in (Types.STRING, Types.LIST) or mismatched:
        raise DispatchError(
            '"concat" cannot be invoked on arguments of type: %s' % (
                ', '.join(arg_types),
            ),
        )

    pieces = [
        val.raw_value  # noqa: no-member
        for val in values
        if not val.is_null  # noqa: no-member
    ]

    return make_value(
        value.data_type,
        six.moves.reduce(lambda x, y: x + y, pieces),
    )


@FUNCTIONS.register(
    'slice',
    (Types.STRING, Types.INTEGER, Types.INTEGER),
    (Types.LIST, Types.INTEGER, Types.INTEGER),
)
def slice_start_end(value, start, end):
    if value.is_empty:
        return value
    return make_value(
        value.data_type,
        value.raw_value[start.raw_value or 0:end.raw_value],
    )


@FUNCTIONS.register(
    'slice',
    (Types.STRING, Types.INTEGER),
    (Types.LIST, Types.INTEGER),
)
def slice_start(value, start):
    if value.is_empty:
        return value
    return make_value(
        value.data_type,
        value.raw_value[start.raw_value or 0:],
    )


@FUNCTIONS.register(
    'at',
    (Types.STRING, Types.INTEGER),
    (Types.LIST, Types.INTEGER),
)
def at_position(value, position):
    if value.is_empty:
        return NULL
    if position.is_null:
        raise ExecutionError('Position cannot be null')

    try:
        val = value.raw_value[position.raw_value]
    except IndexError:
        raise ExecutionError(
            'Position exceeds bounds of sequence',
        )
    if value.data_type == Types.LIST:
        return val
    return make_value(value.data_type, val)

