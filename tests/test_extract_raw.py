import pytest

import streamson

DATA = [b'{"users": ["john","carl","bob"]}']


def test_simple():
    matcher = streamson.SimpleMatcher('{"users"}[]')
    extracted = streamson.extract_iter_raw((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}[0]', b'"john"')
    assert next(extracted) == ('{"users"}[1]', b'"carl"')
    assert next(extracted) == ('{"users"}[2]', b'"bob"')

    with pytest.raises(StopIteration):
        next(extracted)
