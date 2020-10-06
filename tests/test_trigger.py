from enum import Enum, auto

import pytest

import streamson


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
def test_simple(io_reader, data, handler, kind, extract_path):
    hdl, output = handler

    matcher = streamson.SimpleMatcher('{"users"}[]')
    output_data = b""
    if kind == Kind.ITER:
        for e in streamson.trigger_iter((e for e in data), [hdl], matcher, extract_path):
            output_data += e
    elif kind == Kind.FD:
        for e in streamson.trigger_fd(io_reader, [hdl], matcher, 5, extract_path):
            output_data += e
    assert output_data == b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}'
    assert output == [
        ('{"users"}[0]' if extract_path else None, 0, b'"john"'),
        ('{"users"}[1]' if extract_path else None, 0, b'"carl"'),
        ('{"users"}[2]' if extract_path else None, 0, b'"bob"'),
    ]


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
def test_nested(io_reader, data, handler, kind, extract_path):
    hdl, output = handler

    matcher = streamson.SimpleMatcher('{"users"}') | streamson.SimpleMatcher('{"users"}[0]')
    output_data = b""
    if kind == Kind.ITER:
        for e in streamson.trigger_iter((e for e in data), [hdl], matcher, extract_path):
            output_data += e
    elif kind == Kind.FD:
        for e in streamson.trigger_fd(io_reader, [hdl], matcher, 5, extract_path):
            output_data += e
    assert output_data == b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}'
    assert output == [
        ('{"users"}[0]' if extract_path else None, 0, b'"john"'),
        ('{"users"}' if extract_path else None, 0, b'["john", "carl", "bob"]'),
    ]
