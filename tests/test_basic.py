import pytest

import streamson


def test_extract_iter_single():
    data = [b'{"users": ["john","carl","bob"]}']
    extracted = streamson.extract_iter((e for e in data), ['{"users"}[]'])
    assert next(extracted) == ('{"users"}[0]', "john")
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")

    with pytest.raises(StopIteration):
        next(extracted)
