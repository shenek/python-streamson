import io
import json
from enum import Enum, auto

import hyperjson
import pytest

import streamson

DATA = [b'{"users": ["john", "carl", "bob"]}']


class Kind(Enum):
    FD = auto()
    ITER = auto()


@pytest.fixture
def io_reader() -> io.BytesIO:
    return io.BytesIO(b'{"users": ["john", "carl", "bob"]}')


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: json.dumps(x), True),
        (Kind.FD, lambda x: json.dumps(x), False),
        (Kind.FD, lambda x: hyperjson.dumps(x), True),
        (Kind.FD, lambda x: hyperjson.dumps(x), False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: json.dumps(x), True),
        (Kind.ITER, lambda x: json.dumps(x), False),
        (Kind.ITER, lambda x: hyperjson.dumps(x), True),
        (Kind.ITER, lambda x: hyperjson.dumps(x), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-json-path",
        "fd-json-nopath",
        "fd-hyperjson-path",
        "fd-hyperjson-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-json-path",
        "iter-json-nopath",
        "iter-hyperjson-path",
        "iter-hyperjson-nopath",
    ],
)
def test_simple(io_reader, kind, convert, extract_path):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in DATA), matcher, convert, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, 5, convert, extract_path)
    assert next(extracted) == ('{"users"}[0]' if extract_path else None, convert('"john"'))
    assert next(extracted) == ('{"users"}[1]' if extract_path else None, convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]' if extract_path else None, convert('"bob"'))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: json.dumps(x), True),
        (Kind.FD, lambda x: json.dumps(x), False),
        (Kind.FD, lambda x: hyperjson.dumps(x), True),
        (Kind.FD, lambda x: hyperjson.dumps(x), False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: json.dumps(x), True),
        (Kind.ITER, lambda x: json.dumps(x), False),
        (Kind.ITER, lambda x: hyperjson.dumps(x), True),
        (Kind.ITER, lambda x: hyperjson.dumps(x), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-json-path",
        "fd-json-nopath",
        "fd-hyperjson-path",
        "fd-hyperjson-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-json-path",
        "iter-json-nopath",
        "iter-hyperjson-path",
        "iter-hyperjson-nopath",
    ],
)
def test_depth(io_reader, kind, convert, extract_path):
    matcher = streamson.DepthMatcher(1)
    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in DATA), matcher, convert, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, 5, convert, extract_path)
    assert next(extracted) == ('{"users"}[0]' if extract_path else None, convert('"john"'))
    assert next(extracted) == ('{"users"}[1]' if extract_path else None, convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]' if extract_path else None, convert('"bob"'))
    assert next(extracted) == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )
    with pytest.raises(StopIteration):
        next(extracted)

    matcher = streamson.DepthMatcher(0, 1)
    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in DATA), matcher, convert, extract_path)
    elif kind == Kind.FD:
        io_reader.seek(0)
        extracted = streamson.extract_fd(io_reader, matcher, 5, convert, extract_path)
    assert next(extracted) == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )
    assert next(extracted) == (
        "" if extract_path else None,
        convert('{"users": ["john", "carl", "bob"]}'),
    )

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: json.dumps(x), True),
        (Kind.FD, lambda x: json.dumps(x), False),
        (Kind.FD, lambda x: hyperjson.dumps(x), True),
        (Kind.FD, lambda x: hyperjson.dumps(x), False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: json.dumps(x), True),
        (Kind.ITER, lambda x: json.dumps(x), False),
        (Kind.ITER, lambda x: hyperjson.dumps(x), True),
        (Kind.ITER, lambda x: hyperjson.dumps(x), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-json-path",
        "fd-json-nopath",
        "fd-hyperjson-path",
        "fd-hyperjson-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-json-path",
        "iter-json-nopath",
        "iter-hyperjson-path",
        "iter-hyperjson-nopath",
    ],
)
def test_invert(io_reader, kind, convert, extract_path):
    matcher = ~streamson.DepthMatcher(2)
    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in DATA), matcher, convert, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, 5, convert, extract_path)
    assert next(extracted) == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )
    assert next(extracted) == (
        "" if extract_path else None,
        convert('{"users": ["john", "carl", "bob"]}'),
    )


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: json.dumps(x), True),
        (Kind.FD, lambda x: json.dumps(x), False),
        (Kind.FD, lambda x: hyperjson.dumps(x), True),
        (Kind.FD, lambda x: hyperjson.dumps(x), False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: json.dumps(x), True),
        (Kind.ITER, lambda x: json.dumps(x), False),
        (Kind.ITER, lambda x: hyperjson.dumps(x), True),
        (Kind.ITER, lambda x: hyperjson.dumps(x), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-json-path",
        "fd-json-nopath",
        "fd-hyperjson-path",
        "fd-hyperjson-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-json-path",
        "iter-json-nopath",
        "iter-hyperjson-path",
        "iter-hyperjson-nopath",
    ],
)
def test_all(io_reader, kind, convert, extract_path):
    matcher = streamson.SimpleMatcher('{"users"}[]') & streamson.SimpleMatcher("{}[1]")

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in DATA), matcher, convert, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, 5, convert, extract_path)
    assert next(extracted) == ('{"users"}[1]' if extract_path else None, convert('"carl"'))

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: json.dumps(x), True),
        (Kind.FD, lambda x: json.dumps(x), False),
        (Kind.FD, lambda x: hyperjson.dumps(x), True),
        (Kind.FD, lambda x: hyperjson.dumps(x), False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: json.dumps(x), True),
        (Kind.ITER, lambda x: json.dumps(x), False),
        (Kind.ITER, lambda x: hyperjson.dumps(x), True),
        (Kind.ITER, lambda x: hyperjson.dumps(x), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-json-path",
        "fd-json-nopath",
        "fd-hyperjson-path",
        "fd-hyperjson-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-json-path",
        "iter-json-nopath",
        "iter-hyperjson-path",
        "iter-hyperjson-nopath",
    ],
)
def test_any(io_reader, kind, convert, extract_path):
    matcher = streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in DATA), matcher, convert, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, 5, convert, extract_path)
    assert next(extracted) == ('{"users"}[0]' if extract_path else None, convert('"john"'))
    assert next(extracted) == ('{"users"}[1]' if extract_path else None, convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]' if extract_path else None, convert('"bob"'))
    assert next(extracted) == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )

    with pytest.raises(StopIteration):
        next(extracted)


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: json.dumps(x), True),
        (Kind.FD, lambda x: json.dumps(x), False),
        (Kind.FD, lambda x: hyperjson.dumps(x), True),
        (Kind.FD, lambda x: hyperjson.dumps(x), False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: json.dumps(x), True),
        (Kind.ITER, lambda x: json.dumps(x), False),
        (Kind.ITER, lambda x: hyperjson.dumps(x), True),
        (Kind.ITER, lambda x: hyperjson.dumps(x), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-json-path",
        "fd-json-nopath",
        "fd-hyperjson-path",
        "fd-hyperjson-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-json-path",
        "iter-json-nopath",
        "iter-hyperjson-path",
        "iter-hyperjson-nopath",
    ],
)
def test_complex(io_reader, kind, convert, extract_path):
    matcher = (streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')) & ~streamson.SimpleMatcher(
        '{"users"}[0]'
    )

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in DATA), matcher, convert, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, 5, convert, extract_path)
    assert next(extracted) == ('{"users"}[1]' if extract_path else None, convert('"carl"'))
    assert next(extracted) == ('{"users"}[2]' if extract_path else None, convert('"bob"'))
    assert next(extracted) == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )

    with pytest.raises(StopIteration):
        next(extracted)
