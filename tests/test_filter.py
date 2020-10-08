from enum import Enum, auto

import pytest

import streamson


class Kind(Enum):
    FD = auto()
    ITER = auto()


@pytest.mark.parametrize(
    "kind",
    [
        (Kind.FD),
        (Kind.ITER),
    ],
)
def test_simple(io_reader, data, kind):
    matcher = streamson.SimpleMatcher('{"users"}[]')

    output_data = ""
    if kind == Kind.ITER:
        for e in streamson.filter_iter((e for e in data), matcher):
            output_data += e
    elif kind == Kind.FD:
        for e in streamson.filter_fd(io_reader, matcher, 5):
            output_data += e

    assert output_data == '{"users": [], "groups": ["admins", "users"]}'
