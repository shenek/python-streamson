from enum import Enum, auto

import pytest

import streamson


class Kind(Enum):
    FD = auto()
    ITER = auto()


@pytest.mark.parametrize(
    "kind",
    [
        Kind.FD,
        Kind.ITER,
    ],
    ids=[
        "fd",
        "iter",
    ],
)
def test_simple(io_reader, data, replace_handler, kind):

    matcher = streamson.SimpleMatcher('{"users"}[1]')
    output_data = b""
    if kind == Kind.ITER:
        for e in streamson.convert_iter((e for e in data), [(matcher, replace_handler)]):
            if e is not None and e[1] is not None:
                output_data += e[1]
    elif kind == Kind.FD:
        for e in streamson.convert_fd(io_reader, [(matcher, replace_handler)], 5):
            if e is not None and e[1] is not None:
                output_data += e[1]
    assert output_data == b'{"users": ["john", "***", "bob"], "groups": ["admins", "users"]}'
