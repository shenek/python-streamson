from enum import Enum, auto

import pytest

import streamson
from streamson.handler import BufferHandler, PythonConverterHandler
from streamson.output import Output


class Kind(Enum):
    FD = auto()
    ITER = auto()


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, None, True),
        (Kind.FD, None, False),
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), False),
        (Kind.ITER, None, True),
        (Kind.ITER, None, False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-same-path",
        "fd-same-nopath",
        "fd-xx-path",
        "fd-xx-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-same-path",
        "iter-same-nopath",
        "iter-xx-path",
        "iter-xx-nopath",
    ],
)
def test_simple(io_reader, data, kind, convert, extract_path):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in data), matcher, handler, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, handler, 5, extract_path)

    output = Output(extracted).generator()
    assert next(output) == ('{"users"}[0]' if extract_path else None, b'"john"')
    assert next(output) == ('{"users"}[1]' if extract_path else None, b'"carl"')
    assert next(output) == ('{"users"}[2]' if extract_path else None, b'"bob"')

    with pytest.raises(StopIteration):
        next(output)

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == ('{"users"}[0]' if extract_path else None, [e for e in convert(b'"john"')])
    assert buff_handler.pop_front() == ('{"users"}[1]' if extract_path else None, [e for e in convert(b'"carl"')])
    assert buff_handler.pop_front() == ('{"users"}[2]' if extract_path else None, [e for e in convert(b'"bob"')])
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, None, True),
        (Kind.FD, None, False),
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), False),
        (Kind.ITER, None, True),
        (Kind.ITER, None, False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-same-path",
        "fd-same-nopath",
        "fd-xx-path",
        "fd-xx-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-same-path",
        "iter-same-nopath",
        "iter-xx-path",
        "iter-xx-nopath",
    ],
)
def test_depth(io_reader, data, kind, convert, extract_path):
    matcher = streamson.DepthMatcher("1")
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in data), matcher, handler, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, handler, 5, extract_path)

    output = Output(extracted).generator()
    assert next(output) == (
        '{"users"}' if extract_path else None,
        b'["john", "carl", "bob"]',
    )
    assert next(output) == (
        '{"groups"}' if extract_path else None,
        b'["admins", "users"]',
    )
    with pytest.raises(StopIteration):
        next(output)

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}' if extract_path else None,
        [e for e in convert(b'["john", "carl", "bob"]')],
    )
    assert buff_handler.pop_front() == (
        '{"groups"}' if extract_path else None,
        [e for e in convert(b'["admins", "users"]')],
    )
    assert buff_handler.pop_front() is None

    matcher = streamson.DepthMatcher("0")
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler
    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in data), matcher, handler, extract_path)
    elif kind == Kind.FD:
        io_reader.seek(0)
        extracted = streamson.extract_fd(io_reader, matcher, handler, 5, extract_path)

    output = Output(extracted).generator()
    assert next(output) == (
        "" if extract_path else None,
        b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}',
    )

    with pytest.raises(StopIteration):
        next(output)

    assert buff_handler.pop_front() == (
        "" if extract_path else None,
        [e for e in convert(b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, None, True),
        (Kind.FD, None, False),
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), False),
        (Kind.ITER, None, True),
        (Kind.ITER, None, False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-same-path",
        "fd-same-nopath",
        "fd-xx-path",
        "fd-xx-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-same-path",
        "iter-same-nopath",
        "iter-xx-path",
        "iter-xx-nopath",
    ],
)
def test_invert(io_reader, data, kind, convert, extract_path):
    matcher = ~streamson.DepthMatcher("2")
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in data), matcher, handler, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, handler, 5, extract_path)
    output = Output(extracted).generator()

    assert next(output) == (
        "" if extract_path else None,
        b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}',
    )
    with pytest.raises(StopIteration):
        next(output)

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        "" if extract_path else None,
        [e for e in convert(b'{"users": ["john", "carl", "bob"], "groups": ["admins", "users"]}')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, None, True),
        (Kind.FD, None, False),
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), False),
        (Kind.ITER, None, True),
        (Kind.ITER, None, False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-same-path",
        "fd-same-nopath",
        "fd-xx-path",
        "fd-xx-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-same-path",
        "iter-same-nopath",
        "iter-xx-path",
        "iter-xx-nopath",
    ],
)
def test_all(io_reader, data, kind, convert, extract_path):
    matcher = streamson.SimpleMatcher('{"users"}[]') & streamson.SimpleMatcher("{}[1]")
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in data), matcher, handler, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, handler, 5, extract_path)
    output = Output(extracted).generator()

    assert next(output) == ('{"users"}[1]' if extract_path else None, b'"carl"')

    with pytest.raises(StopIteration):
        next(output)

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}[1]' if extract_path else None,
        [e for e in convert(b'"carl"')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, None, True),
        (Kind.FD, None, False),
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), False),
        (Kind.ITER, None, True),
        (Kind.ITER, None, False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-same-path",
        "fd-same-nopath",
        "fd-xx-path",
        "fd-xx-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-same-path",
        "iter-same-nopath",
        "iter-xx-path",
        "iter-xx-nopath",
    ],
)
def test_any(io_reader, data, kind, convert, extract_path):
    matcher = streamson.DepthMatcher("2-2") | streamson.SimpleMatcher('{"users"}')
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in data), matcher, handler, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, handler, 5, extract_path)

    output = Output(extracted).generator()

    assert next(output) == (
        '{"users"}' if extract_path else None,
        b'["john", "carl", "bob"]',
    )
    assert next(output) == (
        '{"groups"}[0]' if extract_path else None,
        b'"admins"',
    )
    assert next(output) == (
        '{"groups"}[1]' if extract_path else None,
        b'"users"',
    )

    with pytest.raises(StopIteration):
        next(output)

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}' if extract_path else None,
        [e for e in convert(b'["john", "carl", "bob"]')],
    )
    assert buff_handler.pop_front() == (
        '{"groups"}[0]' if extract_path else None,
        [e for e in convert(b'"admins"')],
    )
    assert buff_handler.pop_front() == (
        '{"groups"}[1]' if extract_path else None,
        [e for e in convert(b'"users"')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "kind,convert,extract_path",
    [
        (Kind.FD, None, True),
        (Kind.FD, None, False),
        (Kind.FD, lambda x: x, True),
        (Kind.FD, lambda x: x, False),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.FD, lambda x: f"X{x.decode()}X".encode(), False),
        (Kind.ITER, None, True),
        (Kind.ITER, None, False),
        (Kind.ITER, lambda x: x, True),
        (Kind.ITER, lambda x: x, False),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), True),
        (Kind.ITER, lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "fd-raw-path",
        "fd-raw-nopath",
        "fd-same-path",
        "fd-same-nopath",
        "fd-xx-path",
        "fd-xx-nopath",
        "iter-raw-path",
        "iter-raw-nopath",
        "iter-same-path",
        "iter-same-nopath",
        "iter-xx-path",
        "iter-xx-nopath",
    ],
)
def test_complex(io_reader, data, kind, convert, extract_path):
    matcher = (streamson.DepthMatcher("2-2") | streamson.SimpleMatcher('{"users"}')) & ~streamson.SimpleMatcher(
        '{"groups"}[0]'
    )
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    if kind == Kind.ITER:
        extracted = streamson.extract_iter((e for e in data), matcher, handler, extract_path)
    elif kind == Kind.FD:
        extracted = streamson.extract_fd(io_reader, matcher, handler, 55555, extract_path)

    output = Output(extracted).generator()

    assert next(output) == (
        '{"users"}' if extract_path else None,
        b'["john", "carl", "bob"]',
    )
    assert next(output) == (
        '{"groups"}[1]' if extract_path else None,
        b'"users"',
    )

    with pytest.raises(StopIteration):
        next(output)

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}' if extract_path else None,
        [e for e in convert(b'["john", "carl", "bob"]')],
    )
    assert buff_handler.pop_front() == (
        '{"groups"}[1]' if extract_path else None,
        [e for e in convert(b'"users"')],
    )
    assert buff_handler.pop_front() is None
