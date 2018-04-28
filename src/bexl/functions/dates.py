import math

from datetime import date, time, datetime, timedelta

from six import text_type

from ..dispatcher import FUNCTIONS
from ..errors import ExecutionError
from ..types import Types, make_value


@FUNCTIONS.register(
    'date',
    (Types.INTEGER, Types.INTEGER, Types.INTEGER),
)
def make_date(year, month, day):
    year = year.raw_value if not year.is_null else 1
    month = month.raw_value if not month.is_null else 1
    day = day.raw_value if not day.is_null else 1

    try:
        val = date(year, month, day)
    except ValueError as exc:
        raise ExecutionError(text_type(exc))

    return make_value(Types.DATE, val)


@FUNCTIONS.register(
    'time',
    (Types.INTEGER, Types.INTEGER, Types.INTEGER),
    (Types.INTEGER, Types.INTEGER, Types.INTEGER, Types.INTEGER),
)
def make_time(hour, minute, second, millisecond=None):
    hour = hour.raw_value if not hour.is_null else 0
    minute = minute.raw_value if not minute.is_null else 0
    second = second.raw_value if not second.is_null else 0
    if millisecond and not millisecond.is_null:
        millisecond = millisecond.raw_value
    else:
        millisecond = 0

    try:
        val = time(hour, minute, second, millisecond * 1000)
    except ValueError as exc:
        raise ExecutionError(text_type(exc))

    return make_value(Types.TIME, val)


@FUNCTIONS.register(
    'datetime',
    (
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
    ),
    (
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
        Types.INTEGER,
    ),
)
def make_datetime(year, month, day, hour, minute, second, millisecond=None):
    year = year.raw_value if not year.is_null else 1
    month = month.raw_value if not month.is_null else 1
    day = day.raw_value if not day.is_null else 1
    hour = hour.raw_value if not hour.is_null else 0
    minute = minute.raw_value if not minute.is_null else 0
    second = second.raw_value if not second.is_null else 0
    if millisecond and not millisecond.is_null:
        millisecond = millisecond.raw_value
    else:
        millisecond = 0

    try:
        val = datetime(
            year,
            month,
            day,
            hour,
            minute,
            second,
            millisecond * 1000,
        )
    except ValueError as exc:
        raise ExecutionError(text_type(exc))

    return make_value(Types.DATETIME, val)


@FUNCTIONS.register(
    'today',
)
def today():
    return make_value(Types.DATE, date.today())


@FUNCTIONS.register(
    'now',
)
def now():
    return make_value(Types.DATETIME, datetime.now())


@FUNCTIONS.register(
    'year',
    (Types.DATE,),
    (Types.DATETIME,),
)
def get_year(value):
    return make_value(
        Types.INTEGER,
        value.raw_value.year if not value.is_null else None,
    )


@FUNCTIONS.register(
    'month',
    (Types.DATE,),
    (Types.DATETIME,),
)
def get_month(value):
    return make_value(
        Types.INTEGER,
        value.raw_value.month if not value.is_null else None,
    )


@FUNCTIONS.register(
    'day',
    (Types.DATE,),
    (Types.DATETIME,),
)
def get_day(value):
    return make_value(
        Types.INTEGER,
        value.raw_value.day if not value.is_null else None,
    )


@FUNCTIONS.register(
    'hour',
    (Types.TIME,),
    (Types.DATETIME,),
)
def get_hour(value):
    return make_value(
        Types.INTEGER,
        value.raw_value.hour if not value.is_null else None,
    )


@FUNCTIONS.register(
    'minute',
    (Types.TIME,),
    (Types.DATETIME,),
)
def get_minute(value):
    return make_value(
        Types.INTEGER,
        value.raw_value.minute if not value.is_null else None,
    )


@FUNCTIONS.register(
    'second',
    (Types.TIME,),
    (Types.DATETIME,),
)
def get_second(value):
    return make_value(
        Types.INTEGER,
        value.raw_value.second if not value.is_null else None,
    )


@FUNCTIONS.register(
    'millisecond',
    (Types.TIME,),
    (Types.DATETIME,),
)
def get_millisecond(value):
    return make_value(
        Types.INTEGER,
        int(value.raw_value.microsecond / 1000) if not value.is_null else None,
    )


@FUNCTIONS.register(
    'add',
    (Types.DATE, Types.INTEGER),
    (Types.DATE, Types.FLOAT),
    (Types.INTEGER, Types.DATE),
    (Types.FLOAT, Types.DATE),
    (Types.DATETIME, Types.INTEGER),
    (Types.DATETIME, Types.FLOAT),
    (Types.INTEGER, Types.DATETIME),
    (Types.FLOAT, Types.DATETIME),
)
def add_date(left, right):
    if left.data_type in (Types.DATE, Types.DATETIME):
        value = left
        mod = right
    else:
        value = right
        mod = left

    if value.is_null or mod.is_null:
        return make_value(value.data_type, None)

    return make_value(
        value.data_type,
        value.raw_value + timedelta(days=mod.raw_value),
    )


@FUNCTIONS.register(
    'add',
    (Types.TIME, Types.INTEGER),
    (Types.TIME, Types.FLOAT),
    (Types.INTEGER, Types.TIME),
    (Types.FLOAT, Types.TIME),
)
def add_time(left, right):
    if left.data_type == Types.TIME:
        value = left
        mod = right
    else:
        value = right
        mod = left

    if value.is_null or mod.is_null:
        return make_value(value.data_type, None)

    val = datetime.combine(datetime.now(), value.raw_value)
    val = val + timedelta(seconds=mod.raw_value)
    return make_value(value.data_type, val.time())


@FUNCTIONS.register(
    'subtract',
    (Types.DATE, Types.INTEGER),
    (Types.DATE, Types.FLOAT),
    (Types.DATETIME, Types.INTEGER),
    (Types.DATETIME, Types.FLOAT),
)
def subtract_date(left, right):
    if left.is_null or right.is_null:
        return make_value(left.data_type, None)

    if left.data_type == Types.DATE:
        days = math.ceil(right.raw_value)
    else:
        days = right.raw_value

    return make_value(
        left.data_type,
        left.raw_value - timedelta(days=days),
    )


@FUNCTIONS.register(
    'subtract',
    (Types.DATE, Types.DATE),
    (Types.DATE, Types.DATETIME),
    (Types.DATETIME, Types.DATE),
    (Types.DATETIME, Types.DATETIME),
)
def subtract_dates(left, right):
    if left.data_type == Types.DATETIME or right.data_type == Types.DATETIME:
        type_ = Types.FLOAT
    else:
        type_ = Types.INTEGER

    if left.is_null or right.is_null:
        return make_value(type_, None)

    if left.data_type == Types.DATE:
        left = datetime.combine(left.raw_value, time(0, 0, 0))
    else:
        left = left.raw_value
    if right.data_type == Types.DATE:
        right = datetime.combine(right.raw_value, time(0, 0, 0))
    else:
        right = right.raw_value

    diff = (left - right).total_seconds() / (60 * 60 * 24.0)
    if type_ == Types.INTEGER:
        diff = int(diff)

    return make_value(type_, diff)


@FUNCTIONS.register(
    'subtract',
    (Types.TIME, Types.INTEGER),
    (Types.TIME, Types.FLOAT),
)
def subtract_time(left, right):
    if left.is_null or right.is_null:
        return make_value(left.data_type, None)

    val = datetime.combine(datetime.now(), left.raw_value)
    val = val - timedelta(seconds=right.raw_value)
    return make_value(Types.TIME, val.time())


@FUNCTIONS.register(
    'subtract',
    (Types.TIME, Types.TIME),
)
def subtract_times(left, right):
    if left.is_null or right.is_null:
        return make_value(Types.FLOAT, None)

    val = datetime.combine(datetime.now(), left.raw_value)
    val -= datetime.combine(datetime.now(), right.raw_value)
    return make_value(Types.FLOAT, val.total_seconds())

