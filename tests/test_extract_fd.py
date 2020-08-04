import io
import json

import pytest

import streamson


@pytest.fixture
def io_reader() -> io.BytesIO:
    return io.BytesIO(b'{"users": ["john","carl","bob"]}')


def test_simple(io_reader):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    extracted = streamson.extract_fd(io_reader, matcher, convert=json.loads)
    assert next(extracted) == ('{"users"}[0]', "john")
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")

    with pytest.raises(StopIteration):
        next(extracted)


def test_depth(io_reader):
    matcher = streamson.DepthMatcher(1)
    extracted = streamson.extract_fd(io_reader, matcher, convert=json.loads)
    assert next(extracted) == ('{"users"}[0]', "john")
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])

    with pytest.raises(StopIteration):
        next(extracted)

    io_reader.seek(0)
    matcher = streamson.DepthMatcher(0, 1)
    extracted = streamson.extract_fd(io_reader, matcher, convert=json.loads)
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])
    assert next(extracted) == ("", {"users": ["john", "carl", "bob"]})

    with pytest.raises(StopIteration):
        next(extracted)


def test_invert(io_reader):
    matcher = ~streamson.DepthMatcher(2)
    extracted = streamson.extract_fd(io_reader, matcher, convert=json.loads)
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])
    assert next(extracted) == ("", {"users": ["john", "carl", "bob"]})


def test_all(io_reader):
    matcher = streamson.SimpleMatcher('{"users"}[]') & streamson.SimpleMatcher("{}[1]")

    extracted = streamson.extract_fd(io_reader, matcher, convert=json.loads)
    assert next(extracted) == ('{"users"}[1]', "carl")

    with pytest.raises(StopIteration):
        next(extracted)


def test_any(io_reader):
    matcher = streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')

    extracted = streamson.extract_fd(io_reader, matcher, convert=json.loads)
    assert next(extracted) == ('{"users"}[0]', "john")
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])

    with pytest.raises(StopIteration):
        next(extracted)


def test_complex(io_reader):
    matcher = (streamson.DepthMatcher(2, 2) | streamson.SimpleMatcher('{"users"}')) & ~streamson.SimpleMatcher(
        '{"users"}[0]'
    )

    extracted = streamson.extract_fd(io_reader, matcher, convert=json.loads)
    assert next(extracted) == ('{"users"}[1]', "carl")
    assert next(extracted) == ('{"users"}[2]', "bob")
    assert next(extracted) == ('{"users"}', ["john", "carl", "bob"])

    with pytest.raises(StopIteration):
        next(extracted)
