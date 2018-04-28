import decimal
import math
import random

from ..dispatcher import FUNCTIONS
from ..errors import ExecutionError
from ..types import Types, make_value


@FUNCTIONS.register(
    'negative',
    (Types.INTEGER,),
)
def negative_integer(value):
    if value.is_null:
        return value
    return make_value(Types.INTEGER, value.value * -1)


@FUNCTIONS.register(
    'negative',
    (Types.FLOAT,),
)
def negative_float(value):
    if value.is_null:
        return value
    return make_value(Types.FLOAT, value.value * -1.0)


@FUNCTIONS.register(
    'add',
    (Types.INTEGER, Types.INTEGER),
)
def add_integer(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.INTEGER, None)
    return make_value(Types.INTEGER, left.value + right.value)


@FUNCTIONS.register(
    'add',
    (Types.FLOAT, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.FLOAT),
)
def add_float(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.FLOAT, None)
    return make_value(Types.FLOAT, left.value + right.value)


@FUNCTIONS.register(
    'subtract',
    (Types.INTEGER, Types.INTEGER),
)
def subtract_integer(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.INTEGER, None)
    return make_value(Types.INTEGER, left.value - right.value)


@FUNCTIONS.register(
    'subtract',
    (Types.FLOAT, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.FLOAT),
)
def subtract_float(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.FLOAT, None)
    return make_value(Types.FLOAT, left.value - right.value)


@FUNCTIONS.register(
    'multiply',
    (Types.INTEGER, Types.INTEGER),
)
def multiply_integer(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.INTEGER, None)
    return make_value(Types.INTEGER, left.value * right.value)


@FUNCTIONS.register(
    'multiply',
    (Types.FLOAT, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.FLOAT),
)
def multiply_float(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.FLOAT, None)
    return make_value(Types.FLOAT, left.value * right.value)


@FUNCTIONS.register(
    'modulo',
    (Types.INTEGER, Types.INTEGER),
)
def modulo_integer(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.INTEGER, None)
    return make_value(Types.INTEGER, left.value % right.value)


@FUNCTIONS.register(
    'modulo',
    (Types.FLOAT, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.FLOAT),
)
def modulo_float(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.FLOAT, None)
    return make_value(Types.FLOAT, left.value % right.value)


@FUNCTIONS.register(
    'pow',
    (Types.INTEGER, Types.INTEGER),
)
def pow_integer(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.INTEGER, None)
    return make_value(Types.INTEGER, left.value ** right.value)


@FUNCTIONS.register(
    'pow',
    (Types.FLOAT, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.FLOAT),
)
def pow_float(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.FLOAT, None)
    return make_value(Types.FLOAT, left.value ** right.value)


@FUNCTIONS.register(
    'divide',
    (Types.INTEGER, Types.INTEGER),
    (Types.FLOAT, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.FLOAT),
)
def divide(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.FLOAT, None)
    if right.value == 0:
        raise ExecutionError('Cannot divide by zero')
    return make_value(Types.FLOAT, left.value / float(right.value))


@FUNCTIONS.register(
    'abs',
    (Types.INTEGER,),
    (Types.FLOAT,),
)
def func_abs(value):
    if value.is_null:
        return value
    return make_value(value.data_type, abs(value.raw_value))


def simple_func(func, data_type, value):
    if value.is_null:
        return make_value(data_type, None)
    return make_value(data_type, func(value.raw_value))


SIMPLE_FUNCTIONS = (
    ('ceil', math.ceil, Types.INTEGER),
    ('floor', math.floor, Types.INTEGER),
    ('trunc', math.trunc, Types.INTEGER),
    ('sin', math.sin, Types.FLOAT),
    ('cos', math.cos, Types.FLOAT),
    ('tan', math.tan, Types.FLOAT),
    ('sqrt', math.sqrt, Types.FLOAT),
)


for name, impl, dtype in SIMPLE_FUNCTIONS:
    FUNCTIONS.register(name, (Types.INTEGER,), (Types.FLOAT,))(
        lambda value, impl=impl, dtype=dtype: simple_func(
            impl,
            dtype,
            value,
        )
    )


CONST_PI = make_value(Types.FLOAT, math.pi)


@FUNCTIONS.register(
    'pi',
)
def const_pi():
    return CONST_PI


CONST_E = make_value(Types.FLOAT, math.e)


@FUNCTIONS.register(
    'e',
)
def const_e():
    return CONST_E


@FUNCTIONS.register(
    'random',
)
def func_random():
    return make_value(Types.FLOAT, random.random())  # noqa: bandit:B311


@FUNCTIONS.register(
    'log',
    (Types.INTEGER, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.INTEGER),
    (Types.FLOAT, Types.FLOAT),
)
def log(value, base):
    if value.is_null or base.is_null:
        return make_value(Types.FLOAT, None)

    if base.raw_value == 10:
        result = math.log10(value.raw_value)
    else:
        result = math.log(value.raw_value, base.raw_value)

    return make_value(Types.FLOAT, result)


@FUNCTIONS.register(
    'hypot',
    (Types.INTEGER, Types.INTEGER),
    (Types.INTEGER, Types.FLOAT),
    (Types.FLOAT, Types.INTEGER),
    (Types.FLOAT, Types.FLOAT),
)
def hypot(x_value, y_value):
    if x_value.is_null or y_value.is_null:
        return make_value(Types.FLOAT, None)
    return make_value(
        Types.FLOAT,
        math.hypot(x_value.raw_value, y_value.raw_value),
    )


QUANT = decimal.Decimal('1')


def decimal_round(value, precision):
    precision = 10 ** precision
    value *= precision
    value = float(decimal.Decimal(value).quantize(
        QUANT,
        decimal.ROUND_HALF_EVEN,
    ))
    value /= precision
    return value


@FUNCTIONS.register(
    'round',
    (Types.INTEGER,),
    (Types.FLOAT,),
)
def round_integer(value):
    if value.is_null:
        return value
    return make_value(Types.INTEGER, int(decimal_round(value.raw_value, 0)))


@FUNCTIONS.register(
    'round',
    (Types.INTEGER, Types.INTEGER),
    (Types.FLOAT, Types.INTEGER),
)
def round_float(value, precision):
    if value.is_null or precision.is_null:
        return make_value(Types.FLOAT, None)
    return make_value(
        Types.FLOAT,
        decimal_round(value.raw_value, precision.raw_value),
    )

