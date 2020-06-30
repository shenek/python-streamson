import pytest

import streamson

DATA = [b'{"users": ["john","carl","bob"]}']


def test_simple():
    matcher = streamson.SimpleMatcher('{"users"}[]')
    extracted = streamson.extract_iter((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}[0]', "john")
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")

    with pytest.raises(StopIteration):
        next(extracted)


def test_depth():
    matcher = streamson.DepthMatcher(1)
    extracted = streamson.extract_iter((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}[0]', "john")
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])

    with pytest.raises(StopIteration):
        next(extracted)

    matcher = streamson.DepthMatcher(0, 1)
    extracted = streamson.extract_iter((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])
    assert next(extracted) == ("", {"users": ["john", "carl", "bob"]})

    with pytest.raises(StopIteration):
        next(extracted)


def test_invert():
    matcher = ~streamson.DepthMatcher(2)
    extracted = streamson.extract_iter((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])
    assert next(extracted) == ("", {"users": ["john", "carl", "bob"]})


def test_all():
    matcher = streamson.SimpleMatcher('{"users"}[]') & streamson.SimpleMatcher("{}[1]")

    extracted = streamson.extract_iter((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}[1]', "carl")

    with pytest.raises(StopIteration):
        next(extracted)


def test_any():
    matcher = streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')

    extracted = streamson.extract_iter((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}[0]', "john")
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])

    with pytest.raises(StopIteration):
        next(extracted)


def test_complex():
    matcher = (streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')) & ~streamson.SimpleMatcher(
        '{"users"}[0]'
    )

    extracted = streamson.extract_iter((e for e in DATA), matcher)
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])

    with pytest.raises(StopIteration):
        next(extracted)
