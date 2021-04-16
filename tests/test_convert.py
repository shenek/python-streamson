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
def test_simple(io_reader, data, replace_handler, kind, extract_path):

    matcher = streamson.SimpleMatcher('{"users"}[1]')
    output_data = b""
    if kind == Kind.ITER:
        for e in streamson.convert_iter((e for e in data), [(matcher, replace_handler)], extract_path):
            output_data += bytes(e.data or [])
    elif kind == Kind.FD:
        for e in streamson.convert_fd(io_reader, [(matcher, replace_handler)], 5, extract_path):
            output_data += bytes(e.data or [])
    assert output_data == b'{"users": ["john", "***", "bob"], "groups": ["admins", "users"]}'
