import re

from collections import Sequence, Mapping
from datetime import date, time, datetime
from decimal import Decimal

from six import text_type, string_types, integer_types, iteritems, \
    python_2_unicode_compatible

from .enumeration import Enumeration
from .errors import ConversionError, BexlError


class Types(Enumeration):
    UNTYPED = 'untyped'
    STRING = 'string'
    FLOAT = 'float'
    INTEGER = 'integer'
    BOOLEAN = 'boolean'
    DATE = 'date'
    TIME = 'time'
    DATETIME = 'datetime'
    LIST = 'list'
    RECORD = 'record'


def conversion_error(value, data_type):
    raise ConversionError(
        'Cannot convert %s(%s) to %s' % (
            Types.name_for_value(value.data_type),
            value.raw_value,
            Types.name_for_value(data_type),
        ),
        value=value,
        target_type=data_type,
    )


@python_2_unicode_compatible
class Value(object):
    __slots__ = (
        'data_type',
        'raw_value',
    )

    def __init__(self, raw_value):
        self.raw_value = raw_value

    @property
    def value(self):
        return self.raw_value

    @property
    def is_null(self):
        return self.raw_value is None

    @property
    def is_empty(self):
        return self.is_null

    def __eq__(self, other):
        return self.raw_value == other.raw_value

    def __ne__(self, other):
        return self.raw_value != other.raw_value

    def __lt__(self, other):
        return self.raw_value < other.raw_value

    def __le__(self, other):
        return self.raw_value <= other.raw_value

    def __gt__(self, other):
        return self.raw_value > other.raw_value

    def __ge__(self, other):
        return self.raw_value >= other.raw_value

    def __str__(self):
        return text_type(
            'NULL'
            if self.raw_value is None
            else self.raw_value
        )

    def __repr__(self):
        return '%s(%s)' % (
            self.__class__.__name__,
            self,
        )


class UntypedValue(Value):
    data_type = Types.UNTYPED

    def __init__(self, raw_value):
        super(UntypedValue, self).__init__(None)

    @property
    def is_null(self):
        return True


@python_2_unicode_compatible
class StringValue(Value):
    data_type = Types.STRING

    @property
    def is_empty(self):
        return self.is_null or not self.raw_value

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        if value.data_type in (
                Types.INTEGER,
                Types.FLOAT,
                Types.BOOLEAN,
                Types.DATE,
                Types.TIME,
                Types.DATETIME):
            return cls(text_type(value))

        raise conversion_error(value, cls.data_type)

    def __str__(self):
        return text_type(
            'NULL'
            if self.raw_value is None
            else '"%s"' % (self.raw_value,)
        )


class FloatValue(Value):
    data_type = Types.FLOAT

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        if value.data_type in (
                Types.STRING,
                Types.INTEGER):
            try:
                return cls(float(value.raw_value))
            except ValueError:
                raise conversion_error(value, cls.data_type)

        if value.data_type == Types.BOOLEAN:
            return cls(1.0 if value.raw_value else 0.0)

        raise conversion_error(value, cls.data_type)


class IntegerValue(Value):
    data_type = Types.INTEGER

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        if value.data_type in (
                Types.STRING,
                Types.FLOAT):
            try:
                return cls(int(value.raw_value))
            except ValueError:
                raise conversion_error(value, cls.data_type)

        if value.data_type == Types.BOOLEAN:
            return cls(1 if value.raw_value else 0)

        raise conversion_error(value, cls.data_type)


class BooleanValue(Value):
    data_type = Types.BOOLEAN

    @classmethod
    def from_value(cls, value):
        if value.is_empty:
            return cls(False)

        if value.data_type == cls.data_type:
            return cls(value.raw_value)

        if value.data_type in (
                Types.INTEGER,
                Types.FLOAT,
                Types.STRING,
                Types.DATE,
                Types.TIME,
                Types.DATETIME,
                Types.LIST,
                Types.RECORD):
            return cls(True if value.raw_value else False)

        raise conversion_error(value, cls.data_type)


@python_2_unicode_compatible
class ListValue(Value):
    data_type = Types.LIST

    @property
    def is_empty(self):
        return self.is_null or len(self.raw_value) == 0

    @property
    def value(self):
        if self.raw_value is None:
            return None
        return [
            element.value
            for element in self.raw_value
        ]

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        raise conversion_error(value, cls.data_type)

    def __str__(self):
        if self.is_null:
            out = ''
        else:
            out = '[%s]' % (
                ', '.join([
                    text_type(elem)
                    for elem in self.raw_value
                ]),
            )
        return text_type(out)

    def __repr__(self):
        if self.is_null:
            out = 'NULL'
        else:
            out = ', '.join([
                repr(elem)
                for elem in self.raw_value
            ])
        return '%s(%s)' % (
            self.__class__.__name__,
            out,
        )


@python_2_unicode_compatible
class RecordValue(Value):
    data_type = Types.RECORD

    @property
    def is_empty(self):
        return self.is_null or len(self.raw_value) == 0

    @property
    def value(self):
        if self.raw_value is None:
            return None
        return dict([
            (prop, element.value)
            for prop, element in iteritems(self.raw_value)
        ])

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        raise conversion_error(value, cls.data_type)

    def __str__(self):
        if self.is_null:
            out = ''
        else:
            out = '{%s}' % (
                ', '.join([
                    '%s: %s' % (name, text_type(value))
                    for name, value in iteritems(self.raw_value)
                ]),
            )
        return text_type(out)

    def __repr__(self):
        if self.is_null:
            out = 'NULL'
        else:
            out = ', '.join([
                '%s: %s' % (name, repr(value))
                for name, value in iteritems(self.raw_value)
            ])
        return '%s(%s)' % (
            self.__class__.__name__,
            out,
        )


@python_2_unicode_compatible
class DateValue(Value):
    data_type = Types.DATE

    REGEX = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        if value.data_type == Types.STRING:
            try:
                return cls(
                    datetime.strptime(value.raw_value, '%Y-%m-%d').date()
                )
            except ValueError:
                raise conversion_error(value, cls.data_type)

        if value.data_type == Types.DATETIME:
            return cls(value.raw_value.date())

        raise conversion_error(value, cls.data_type)

    def __str__(self):
        return text_type(
            ''
            if self.raw_value is None
            else self.raw_value.isoformat()
        )


TIME_FORMATS = (
    '%H:%M:%S.%f',
    '%H:%M:%S',
    '%H:%M',
)


@python_2_unicode_compatible
class TimeValue(Value):
    data_type = Types.TIME

    REGEX = re.compile(r'^\d{2}:\d{2}(:\d{2}(\.\d{3})?)?$')

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        if value.data_type == Types.STRING:
            for time_format in TIME_FORMATS:
                try:
                    return cls(
                        datetime.strptime(value.raw_value, time_format).time()
                    )
                except ValueError:
                    continue
            raise conversion_error(value, cls.data_type)

        if value.data_type == Types.DATETIME:
            return cls(value.raw_value.time())

        raise conversion_error(value, cls.data_type)

    def __str__(self):
        return text_type(
            ''
            if self.raw_value is None
            else self.raw_value.isoformat()
        )


DATETIME_FORMATS = (
    '%Y-%m-%dT%H:%M:%S.%f',
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%d',
)


@python_2_unicode_compatible
class DateTimeValue(Value):
    data_type = Types.DATETIME

    REGEX = re.compile(
        r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2}(\.\d{3})?)?)?$'
    )

    @classmethod
    def from_value(cls, value):
        if value.data_type == cls.data_type or value.is_null:
            return cls(value.raw_value)

        if value.data_type == Types.STRING:
            for dt_format in DATETIME_FORMATS:
                try:
                    return cls(datetime.strptime(value.raw_value, dt_format))
                except ValueError:
                    continue
            raise conversion_error(value, cls.data_type)

        if value.data_type == Types.DATE:
            return cls(datetime(
                value.raw_value.year,
                value.raw_value.month,
                value.raw_value.day,
            ))

        raise conversion_error(value, cls.data_type)

    def __str__(self):
        return text_type(
            ''
            if self.raw_value is None
            else self.raw_value.isoformat('T')
        )


_TYPE_VALUES = {
    Types.UNTYPED: UntypedValue,
    Types.STRING: StringValue,
    Types.FLOAT: FloatValue,
    Types.INTEGER: IntegerValue,
    Types.BOOLEAN: BooleanValue,
    Types.LIST: ListValue,
    Types.RECORD: RecordValue,
    Types.DATE: DateValue,
    Types.TIME: TimeValue,
    Types.DATETIME: DateTimeValue,
}


def make_value(data_type, raw_value):
    value_type = _TYPE_VALUES.get(data_type)
    if not value_type:
        raise ConversionError(
            'Unknown data type %s' % (
                Types.name_for_value(data_type),
            )
        )
    return value_type(raw_value)


def cast(value, data_type):
    if value.data_type == data_type:
        return value
    return _TYPE_VALUES[data_type].from_value(value)


def is_consistently_typed(values, types=None):
    if not values:
        return True

    vtypes = [value.data_type for value in values]

    if not types:
        types = (vtypes[0],)

    wrong = [vtype for vtype in vtypes if vtype not in types]

    return False if wrong else True


TRUE = BooleanValue(True)
FALSE = BooleanValue(False)
NULL = UntypedValue(None)


_NATIVE_TYPES = {
    type(None): Types.UNTYPED,
    bool: Types.BOOLEAN,
    date: Types.DATE,
    time: Types.TIME,
    datetime: Types.DATETIME,
}


def python_to_bexl(value):
    """
    Converts a native Python value to a BEXL Value. Useful when providing
    variable values to the BEXL Interpreter.

    :param value: the value to convert
    :type value: any
    :rtype: bexl.types.Value
    :raises: BexlError if the value cannot be converted
    """

    for ptype, btype in iteritems(_NATIVE_TYPES):
        if isinstance(value, ptype):
            return make_value(btype, value)

    if isinstance(value, Value):
        return value

    elif isinstance(value, integer_types):
        return make_value(Types.INTEGER, value)

    elif isinstance(value, (float, Decimal)):
        return make_value(Types.FLOAT, float(value))

    elif isinstance(value, string_types):
        return make_value(Types.STRING, text_type(value))

    elif isinstance(value, Sequence):
        return make_value(Types.LIST, [
            python_to_bexl(element)
            for element in value
        ])

    elif isinstance(value, Mapping):
        return make_value(Types.RECORD, dict([
            (key, python_to_bexl(value[key]))
            for key in value
        ]))

    raise BexlError(
        'Cannot create a BEXL value from %r' % (value)
    )


def bexl_to_python(value):
    """
    Converts a BEXL Value to a native Python value.

    :param value: the value to convert
    :type value: bexl.types.Value
    """

    return value.value

