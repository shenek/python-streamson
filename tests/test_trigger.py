from enum import Enum, auto

import pytest
import streamson
from streamson.handler import BufferHandler


class Kind(Enum):
    FD = auto()
    ITER = auto()


@pytest.mark.parametrize(
    "kind,extract_path",
    [
        (Kind.FD, True),
        (Kind.FD, False),
        (Kind.ITER, True),
        (Kind.ITER, False),
    ],
    ids=[
        "fd-path",
        "fd-nopath",
        "iter-path",
        "iter-nopath",
    ],
)
def test_simple(io_reader, data, kind, extract_path):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    handler = BufferHandler(use_path=extract_path)
    output_data = b""
    if kind == Kind.ITER:
        for e in streamson.trigger_iter((e for e in data), [(matcher, handler)], extract_path):
            output_data += e
    elif kind == Kind.FD:
        for e in streamson.trigger_fd(io_reader, [(matcher, handler)], 5, extract_path):
            output_data += e

    assert output_data == b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}'

    assert handler.pop_front() == ('{"users"}[0]' if extract_path else None, [e for e in b'"john"'])
    assert handler.pop_front() == ('{"users"}[1]' if extract_path else None, [e for e in b'"carl"'])
    assert handler.pop_front() == ('{"users"}[2]' if extract_path else None, [e for e in b'"bob"'])
    assert handler.pop_front() is None


@pytest.mark.skip("Nested matches seems to be broken in streamson-lib")
@pytest.mark.parametrize(
    "kind,extract_path",
    [
        (Kind.FD, True),
        (Kind.FD, False),
        (Kind.ITER, True),
        (Kind.ITER, False),
    ],
    ids=[
        "fd-path",
        "fd-nopath",
        "iter-path",
        "iter-nopath",
    ],
)
def test_nested(io_reader, data, kind, extract_path):
    handler = BufferHandler(use_path=extract_path)

    matcher = streamson.SimpleMatcher('{"users"}') | streamson.SimpleMatcher('{"users"}[0]')
    output_data = b""
    if kind == Kind.ITER:
        for e in streamson.trigger_iter((e for e in data), [(matcher, handler)], extract_path):
            output_data += e
    elif kind == Kind.FD:
        for e in streamson.trigger_fd(io_reader, [(matcher, handler)], 5, extract_path):
            output_data += e
    assert output_data == b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}'

    assert handler.pop_front() == ('{"users"}[0]' if extract_path else None, [e for e in b'"john"'])
    assert handler.pop_front() == ('{"users"}' if extract_path else None, [e for e in b'["john", "carl", "bob"]'])
    assert handler.pop_front() is None
