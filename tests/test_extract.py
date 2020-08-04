import json

import pytest

import streamson

DATA = [b'{"users": ["john", "carl", "bob"]}']


@pytest.mark.parametrize(
    "parse,convert", [(True, lambda x: x), (False, lambda x: json.dumps(x))], ids=["parse", "raw"],
)
def test_simple(parse, convert):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    extracted = streamson.extract_iter((e for e in DATA), matcher, parse)
    assert next(extracted) == ('{"users"}[0]', convert("john"))
    assert next(extracted) == ('{"users"}[1]', convert("carl"))
    assert next(extracted) == ('{"users"}[2]', convert("bob"))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "parse,convert", [(True, lambda x: x), (False, lambda x: json.dumps(x))], ids=["parse", "raw"],
)
def test_depth(parse, convert):
    matcher = streamson.DepthMatcher(1)
    extracted = streamson.extract_iter((e for e in DATA), matcher, parse)
    assert next(extracted) == ('{"users"}[0]', convert("john"))
    assert next(extracted) == ('{"users"}[1]', convert("carl"))
    assert next(extracted) == ('{"users"}[2]', convert("bob"))
    assert next(extracted) == ('{"users"}', convert(["john", "carl", "bob"]))
    with pytest.raises(StopIteration):
        next(extracted)

    matcher = streamson.DepthMatcher(0, 1)
    extracted = streamson.extract_iter((e for e in DATA), matcher, parse)
    assert next(extracted) == ('{"users"}', convert(["john", "carl", "bob"]))
    assert next(extracted) == ("", convert({"users": ["john", "carl", "bob"]}))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "parse,convert", [(True, lambda x: x), (False, lambda x: json.dumps(x))], ids=["parse", "raw"],
)
def test_invert(parse, convert):
    matcher = ~streamson.DepthMatcher(2)
    extracted = streamson.extract_iter((e for e in DATA), matcher, parse)
    assert next(extracted) == ('{"users"}', convert(["john", "carl", "bob"]))
    assert next(extracted) == ("", convert({"users": ["john", "carl", "bob"]}))


@pytest.mark.parametrize(
    "parse,convert", [(True, lambda x: x), (False, lambda x: json.dumps(x))], ids=["parse", "raw"],
)
def test_all(parse, convert):
    matcher = streamson.SimpleMatcher('{"users"}[]') & streamson.SimpleMatcher("{}[1]")

    extracted = streamson.extract_iter((e for e in DATA), matcher, parse)
    assert next(extracted) == ('{"users"}[1]', convert("carl"))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "parse,convert", [(True, lambda x: x), (False, lambda x: json.dumps(x))], ids=["parse", "raw"],
)
def test_any(parse, convert):
    matcher = streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')

    extracted = streamson.extract_iter((e for e in DATA), matcher, parse)
    assert next(extracted) == ('{"users"}[0]', convert("john"))
    assert next(extracted) == ('{"users"}[1]', convert("carl"))
    assert next(extracted) == ('{"users"}[2]', convert("bob"))
    assert next(extracted) == ('{"users"}', convert(["john", "carl", "bob"]))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "parse,convert", [(True, lambda x: x), (False, lambda x: json.dumps(x))], ids=["parse", "raw"],
)
def test_complex(parse, convert):
    matcher = (streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')) & ~streamson.SimpleMatcher(
        '{"users"}[0]'
    )

    extracted = streamson.extract_iter((e for e in DATA), matcher, parse)
    assert next(extracted) == ('{"users"}[1]', convert("carl"))
    assert next(extracted) == ('{"users"}[2]', convert("bob"))
    assert next(extracted) == ('{"users"}', convert(["john", "carl", "bob"]))

    with pytest.raises(StopIteration):
        next(extracted)
