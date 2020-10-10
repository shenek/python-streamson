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
def test_simple(io_reader, data, converter, kind, extract_path):

    matcher = streamson.SimpleMatcher('{"users"}[1]')
    output_data = ""
    if kind == Kind.ITER:
        for e in streamson.convert_iter((e for e in data), [converter], matcher, extract_path):
            output_data += e
    elif kind == Kind.FD:
        for e in streamson.convert_fd(io_reader, [converter], matcher, 5, extract_path):
            output_data += e
    assert output_data == '{"users": ["john", "***", "bob"], "groups": ["admins", "users"]}'
