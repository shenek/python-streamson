from enum import Enum, auto

import pytest

import streamson
from streamson.handler import AnalyserHandler, IndenterHandler
from streamson.output import Output


class Kind(Enum):
    FD = auto()
    ITER = auto()


@pytest.mark.parametrize(
    "kind,convert",
    [
        (Kind.FD, True),
        (Kind.FD, False),
        (Kind.ITER, True),
        (Kind.ITER, False),
    ],
    ids=[
        "fd-convert",
        "fd-noconvert",
        "iter-convert",
        "iter-noconvert",
    ],
)
def test_basic(io_reader, data, kind, convert):
    analyser_handler = AnalyserHandler()
    handler = analyser_handler + IndenterHandler(None) if convert else analyser_handler

    if kind == Kind.ITER:
        processed = streamson.all_iter((e for e in data), [handler], convert)
    elif kind == Kind.FD:
        processed = streamson.all_fd(io_reader, [handler], convert, 5)

    output = Output(processed).generator()
    if convert:
        assert next(output) == (None, b'{"users":["john","carl","bob"],"groups":["admins","users"]}')

    with pytest.raises(StopIteration):
        next(output)

    assert analyser_handler.results() == [
        ("", 1),
        ('{"groups"}', 1),
        ('{"groups"}[]', 2),
        ('{"users"}', 1),
        ('{"users"}[]', 3),
    ]
