import pytest

import streamson

DATA = [b'{"users": ["john","carl","bob"]}']


def test_simple():
    matcher = streamson.SimpleMatcher('{"users"}[]')
    extracted = streamson.extract_iter_raw((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}[0]', '"john"')
    assert next(extracted) == ('{"users"}[1]', '"carl"')
    assert next(extracted) == ('{"users"}[2]', '"bob"')

    with pytest.raises(StopIteration):
        next(extracted)
