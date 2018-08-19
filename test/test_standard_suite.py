import os

import pytest
import yaml

from bexl import evaluate, bexl_to_python, python_to_bexl, VariableResolver, \
    IntegerValue, FloatValue, StringValue, BooleanValue, ListValue, \
    UntypedValue, RecordValue, DateValue, TimeValue, DateTimeValue, BexlError


NoneType = type(None)


TESTS = [
    (
        group['desc'],
        test['desc'],
        test,
    )
    for group in yaml.load(
        open(os.path.join(os.path.dirname(__file__), 'standard_test_suite.yaml'))
    )['suite']
    for test in group['tests']
]


TYPES = {
    'INTEGER': IntegerValue,
    'FLOAT': FloatValue,
    'STRING': StringValue,
    'BOOLEAN': BooleanValue,
    'LIST': ListValue,
    'RECORD': RecordValue,
    'UNTYPED': UntypedValue,
    'DATE': DateValue,
    'TIME': TimeValue,
    'DATETIME': DateTimeValue,
}


def make_value(value, type):
    if value is None:
        return TYPES[type](value)
    if type == 'LIST':
        return ListValue([
            python_to_bexl(element)
            for element in value
        ])
    if type == 'RECORD':
        return RecordValue(dict([
            (key, python_to_bexl(value))
            for key, value in value.items()
        ]))
    return TYPES[type](value)


def make_native(spec):
    if spec['type'] in ('DATE', 'TIME', 'DATETIME'):
        return TYPES[spec['type']].from_value(StringValue(spec['value'])).raw_value
    return spec['value']


@pytest.mark.parametrize('group_name,test_name,test', TESTS)
def test_standard_suite(group_name, test_name, test):
    var_res = VariableResolver()
    for var, defn in test.get('vars', {}).items():
        var_res[var] = make_value(defn['value'], defn['type'])

    try:
        actual = evaluate(test['expr'], native=False, variable_resolver=var_res)
    except BexlError:
        if 'error' not in test:
            raise
    else:
        if 'value' in test['result']:
            if test['result']['type'] == 'FLOAT' and test['result']['value'] is not None:
                assert bexl_to_python(actual) == pytest.approx(make_native(test['result']), abs=1e-13)
            else:
                assert bexl_to_python(actual) == make_native(test['result'])
        assert actual.data_type == test['result']['type'].lower()

