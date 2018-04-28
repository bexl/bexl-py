from ..dispatcher import FUNCTIONS
from ..errors import ExecutionError
from ..types import Types, make_value, cast, TRUE, FALSE, NULL


FULL_SPECS = (
    ('integer', Types.INTEGER),
    ('float', Types.FLOAT),
    ('boolean', Types.BOOLEAN),
    ('string', Types.STRING),
)

IS_SPECS = (
    ('date', Types.DATE),
    ('time', Types.TIME),
    ('datetime', Types.DATETIME),
    ('list', Types.LIST),
    ('record', Types.RECORD),
)

for name, data_type in FULL_SPECS:
    FUNCTIONS.register(name)(
        lambda value, data_type=data_type: cast(value, data_type)
    )

for name, data_type in FULL_SPECS + IS_SPECS:
    FUNCTIONS.register('is%s' % (name.capitalize(),))(
        lambda value, data_type=data_type:
        TRUE if value.data_type == data_type else FALSE
    )


@FUNCTIONS.register(
    'isNull',
)
def is_null(value):
    return TRUE if value.is_null else FALSE


@FUNCTIONS.register(
    'list',
)
def type_list(*values):
    return make_value(Types.LIST, values)


@FUNCTIONS.register(
    'record',
)
def type_record(*values):
    if not values or len(values) % 2 != 0:
        raise ExecutionError(
            'Incorrect number of arguments'
        )

    value = {}
    for i in range(0, len(values), 2):
        if values[i].data_type != Types.STRING:
            raise ExecutionError(
                'Property names must be a string, not %s' % (
                    values[i].data_type,
                ),
            )
        if values[i].is_null:
            raise ExecutionError('Property names cannot be null')

        value[values[i].raw_value] = values[i + 1]

    return make_value(Types.RECORD, value)


@FUNCTIONS.register(
    'date',
    (Types.INTEGER,),
    (Types.FLOAT,),
    (Types.STRING,),
    (Types.BOOLEAN,),
    (Types.DATE,),
    (Types.TIME,),
    (Types.DATETIME,),
    (Types.LIST,),
    (Types.RECORD,),
    (Types.UNTYPED,),
)
def type_date(value):
    return cast(value, Types.DATE)


@FUNCTIONS.register(
    'time',
    (Types.INTEGER,),
    (Types.FLOAT,),
    (Types.STRING,),
    (Types.BOOLEAN,),
    (Types.DATE,),
    (Types.TIME,),
    (Types.DATETIME,),
    (Types.LIST,),
    (Types.RECORD,),
    (Types.UNTYPED,),
)
def type_time(value):
    return cast(value, Types.TIME)


@FUNCTIONS.register(
    'datetime',
    (Types.INTEGER,),
    (Types.FLOAT,),
    (Types.STRING,),
    (Types.BOOLEAN,),
    (Types.DATE,),
    (Types.TIME,),
    (Types.DATETIME,),
    (Types.LIST,),
    (Types.RECORD,),
    (Types.UNTYPED,),
)
def type_datetime(value):
    return cast(value, Types.DATETIME)


@FUNCTIONS.register(
    'property',
    (Types.RECORD, Types.STRING),
)
def property_access(record, prop):
    if record.is_null:
        return NULL
    if prop.is_null:
        raise ExecutionError('Property cannot be null')

    value = record.raw_value.get(prop.raw_value)
    if not value:
        raise ExecutionError(
            'Record does not contain a property named "%s"' % (
                prop.raw_value,
            )
        )

    return value


@FUNCTIONS.register(
    'coalesce',
)
def coalesce(*values):
    for value in values:
        if not value.is_null:
            return value
    return NULL

