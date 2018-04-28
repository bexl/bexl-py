from ..dispatcher import FUNCTIONS
from ..errors import ExecutionError
from ..types import Types, make_value


@FUNCTIONS.register(
    'upper',
    (Types.STRING,),
)
def upper(value):
    if value.is_empty:
        return value
    return make_value(Types.STRING, value.raw_value.upper())


@FUNCTIONS.register(
    'lower',
    (Types.STRING,),
)
def lower(value):
    if value.is_empty:
        return value
    return make_value(Types.STRING, value.raw_value.lower())


@FUNCTIONS.register(
    'trim',
    (Types.STRING,),
)
def trim(value):
    if value.is_empty:
        return value
    return make_value(Types.STRING, value.raw_value.strip())


@FUNCTIONS.register(
    'ltrim',
    (Types.STRING,),
)
def ltrim(value):
    if value.is_empty:
        return value
    return make_value(Types.STRING, value.raw_value.lstrip())


@FUNCTIONS.register(
    'rtrim',
    (Types.STRING,),
)
def rtrim(value):
    if value.is_empty:
        return value
    return make_value(Types.STRING, value.raw_value.rstrip())


@FUNCTIONS.register(
    'replace',
    (Types.STRING, Types.STRING, Types.STRING),
)
def replace(value, needle, replacement):
    if value.is_empty or needle.is_empty:
        return value
    return make_value(
        Types.STRING,
        value.raw_value.replace(needle.raw_value, replacement.raw_value or ''),
    )


@FUNCTIONS.register(
    'repeat',
    (Types.STRING, Types.INTEGER),
)
def repeat(value, repetitions):
    if value.is_empty or repetitions.is_null:
        return value

    if repetitions.raw_value < 0:
        raise ExecutionError('Repetitions cannot be negative')

    return make_value(Types.STRING, value.raw_value * repetitions.raw_value)

