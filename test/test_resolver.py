import pytest

from bexl import VariableResolver, BexlError


def test_make_from_none():
    vr = VariableResolver.make_from(None)
    assert isinstance(vr, VariableResolver)
    assert len(vr) == 0
    assert len(vr.keys()) == 0


def test_make_from_resolver():
    vr = VariableResolver(foo=123)
    vr2 = VariableResolver.make_from(vr)
    assert isinstance(vr2, VariableResolver)
    assert len(vr2) == 1
    assert len(vr2.keys()) == 1
    assert vr2['foo'].value == 123


def test_make_from_map():
    vr = VariableResolver.make_from({'foo': 123, 'bar': True})
    assert isinstance(vr, VariableResolver)
    assert len(vr) == 2
    assert len(vr.keys()) == 2
    assert vr['foo'].value == 123
    assert vr['bar'].value == True


def test_make_from_garbage():
    with pytest.raises(BexlError):
        VariableResolver.make_from(123)


def test_get_value():
    vr = VariableResolver(foo=123)
    assert vr['foo'].value == 123
    assert vr('foo').value == 123

    with pytest.raises(BexlError):
        vr('bar')
    with pytest.raises(KeyError):
        vr['bar']


def test_set_value():
    vr = VariableResolver()
    vr['foo'] = 123
    assert vr['foo'].value == 123


def test_del_value():
    vr = VariableResolver(foo=123)
    del vr['foo']
    with pytest.raises(KeyError):
        vr['foo']

