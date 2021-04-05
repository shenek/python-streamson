from enum import Enum, auto

import pytest
import streamson
from streamson.handler import BufferHandler, PythonConverterHandler
from streamson.output import Output


class Kind(Enum):
    FD = auto()
    ITER = auto()


@pytest.mark.parametrize(
    "kind,convert",
    [
        (Kind.FD, None),
        (Kind.FD, lambda x: x),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode()),
        (Kind.ITER, None),
        (Kind.ITER, lambda x: x),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode()),
    ],
    ids=[
        "fd-raw",
        "fd-same",
        "fd-xx",
        "iter-raw",
        "iter-same",
        "iter-xx",
    ],
)
def test_simple(io_reader, data, kind, convert):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    buff_handler = BufferHandler()
    handler = PythonConverterHandler(convert) + buff_handler if convert else buff_handler

    if kind == Kind.ITER:
        filtered = streamson.filter_iter((e for e in data), matcher, handler)
    elif kind == Kind.FD:
        filtered = streamson.filter_fd(io_reader, matcher, handler, 5)

    output = Output(filtered).generator()
    assert next(output) == (None, b'{"users": [], "groups": ["admins", "users"]}')
    with pytest.raises(StopIteration):
        next(output)

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == ('{"users"}[0]', [e for e in convert(b'"john"')])
    assert buff_handler.pop_front() == ('{"users"}[1]', [e for e in convert(b'"carl"')])
    assert buff_handler.pop_front() == ('{"users"}[2]', [e for e in convert(b'"bob"')])
    assert buff_handler.pop_front() is None
