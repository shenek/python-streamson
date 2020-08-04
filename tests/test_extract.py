import json

import hyperjson
import pytest

import streamson

DATA = [b'{"users": ["john", "carl", "bob"]}']


@pytest.mark.parametrize(
    "convert", [lambda x: x, lambda x: json.dumps(x), lambda x: hyperjson.dumps(x)], ids=["raw", "json", "hyperjson"],
)
def test_simple(convert):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    extracted = streamson.extract_iter((e for e in DATA), matcher, convert)
    assert next(extracted) == ('{"users"}[0]', convert('"john"'))
    assert next(extracted) == ('{"users"}[1]', convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]', convert('"bob"'))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "convert", [lambda x: x, lambda x: json.dumps(x), lambda x: hyperjson.dumps(x)], ids=["raw", "json", "hyperjson"],
)
def test_depth(convert):
    matcher = streamson.DepthMatcher(1)
    extracted = streamson.extract_iter((e for e in DATA), matcher, convert)
    assert next(extracted) == ('{"users"}[0]', convert('"john"'))
    assert next(extracted) == ('{"users"}[1]', convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]', convert('"bob"'))
    assert next(extracted) == ('{"users"}', convert('["john", "carl", "bob"]'))
    with pytest.raises(StopIteration):
        next(extracted)

    matcher = streamson.DepthMatcher(0, 1)
    extracted = streamson.extract_iter((e for e in DATA), matcher, convert)
    assert next(extracted) == ('{"users"}', convert('["john", "carl", "bob"]'))
    assert next(extracted) == ("", convert('{"users": ["john", "carl", "bob"]}'))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "convert", [lambda x: x, lambda x: json.dumps(x), lambda x: hyperjson.dumps(x)], ids=["raw", "json", "hyperjson"],
)
def test_invert(convert):
    matcher = ~streamson.DepthMatcher(2)
    extracted = streamson.extract_iter((e for e in DATA), matcher, convert)
    assert next(extracted) == ('{"users"}', convert('["john", "carl", "bob"]'))
    assert next(extracted) == ("", convert('{"users": ["john", "carl", "bob"]}'))


@pytest.mark.parametrize(
    "convert", [lambda x: x, lambda x: json.dumps(x), lambda x: hyperjson.dumps(x)], ids=["raw", "json", "hyperjson"],
)
def test_all(convert):
    matcher = streamson.SimpleMatcher('{"users"}[]') & streamson.SimpleMatcher("{}[1]")

    extracted = streamson.extract_iter((e for e in DATA), matcher, convert)
    assert next(extracted) == ('{"users"}[1]', convert('"carl"'))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "convert", [lambda x: x, lambda x: json.dumps(x), lambda x: hyperjson.dumps(x)], ids=["raw", "json", "hyperjson"],
)
def test_any(convert):
    matcher = streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')

    extracted = streamson.extract_iter((e for e in DATA), matcher, convert)
    assert next(extracted) == ('{"users"}[0]', convert('"john"'))
    assert next(extracted) == ('{"users"}[1]', convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]', convert('"bob"'))
    assert next(extracted) == ('{"users"}', convert('["john", "carl", "bob"]'))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "convert", [lambda x: x, lambda x: json.dumps(x), lambda x: hyperjson.dumps(x)], ids=["raw", "json", "hyperjson"],
)
def test_complex(convert):
    matcher = (streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')) & ~streamson.SimpleMatcher(
        '{"users"}[0]'
    )

    extracted = streamson.extract_iter((e for e in DATA), matcher, convert)
    assert next(extracted) == ('{"users"}[1]', convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]', convert('"bob"'))
    assert next(extracted) == ('{"users"}', convert('["john", "carl", "bob"]'))

    with pytest.raises(StopIteration):
        next(extracted)
