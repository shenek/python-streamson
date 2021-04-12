import pytest

import streamson
from streamson.handler import BufferHandler, PythonConverterHandler
from streamson.output import Output


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (None, True),
        (None, False),
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: f"X{x.decode()}X".encode(), True),
        (lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "raw-path",
        "raw-nopath",
        "json-path",
        "json-nopath",
        "hyperjson-path",
        "hyperjson-nopath",
    ],
)
@pytest.mark.asyncio
async def test_simple(make_async_gen, convert, extract_path):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    async_out = streamson.extract_async(make_async_gen()(), matcher, handler, extract_path)

    res = []

    async for rec in async_out:
        res.append(rec)

    output = list(Output(e for e in res).generator())
    assert len(output) == 3

    assert output[0] == ('{"users"}[0]' if extract_path else None, b'"john"')
    assert output[1] == ('{"users"}[1]' if extract_path else None, b'"carl"')
    assert output[2] == ('{"users"}[2]' if extract_path else None, b'"bob"')

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}[0]' if extract_path else None,
        [e for e in convert(b'"john"')],
    )
    assert buff_handler.pop_front() == (
        '{"users"}[1]' if extract_path else None,
        [e for e in convert(b'"carl"')],
    )
    assert buff_handler.pop_front() == (
        '{"users"}[2]' if extract_path else None,
        [e for e in convert(b'"bob"')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (None, True),
        (None, False),
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: f"X{x.decode()}X".encode(), True),
        (lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "raw-path",
        "raw-nopath",
        "json-path",
        "json-nopath",
        "hyperjson-path",
        "hyperjson-nopath",
    ],
)
@pytest.mark.asyncio
async def test_depth(make_async_gen, convert, extract_path):
    matcher = streamson.DepthMatcher("1")
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    async_out = streamson.extract_async(make_async_gen()(), matcher, handler, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    output = list(Output(e for e in res).generator())

    assert len(output) == 1

    assert output[0] == (
        '{"users"}' if extract_path else None,
        b'["john", "carl", "bob"]',
    )

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}' if extract_path else None,
        [e for e in convert(b'["john", "carl", "bob"]')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (None, True),
        (None, False),
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: f"X{x.decode()}X".encode(), True),
        (lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "raw-path",
        "raw-nopath",
        "json-path",
        "json-nopath",
        "hyperjson-path",
        "hyperjson-nopath",
    ],
)
@pytest.mark.asyncio
async def test_invert(make_async_gen, convert, extract_path):
    matcher = ~streamson.DepthMatcher("2")
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler
    async_out = streamson.extract_async(make_async_gen()(), matcher, handler, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    output = list(Output(e for e in res).generator())

    assert len(output) == 1

    assert output[0] == (
        "" if extract_path else None,
        b'{"users": ["john", "carl", "bob"]}',
    )

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        "" if extract_path else None,
        [e for e in convert(b'{"users": ["john", "carl", "bob"]}')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (None, True),
        (None, False),
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: f"X{x.decode()}X".encode(), True),
        (lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "raw-path",
        "raw-nopath",
        "json-path",
        "json-nopath",
        "hyperjson-path",
        "hyperjson-nopath",
    ],
)
@pytest.mark.asyncio
async def test_all(make_async_gen, convert, extract_path):
    matcher = streamson.SimpleMatcher('{"users"}[]') & streamson.SimpleMatcher("{}[1]")
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    async_out = streamson.extract_async(make_async_gen()(), matcher, handler, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    output = list(Output(e for e in res).generator())

    assert len(output) == 1

    assert output[0] == ('{"users"}[1]' if extract_path else None, b'"carl"')

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}[1]' if extract_path else None,
        [e for e in convert(b'"carl"')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (None, True),
        (None, False),
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: f"X{x.decode()}X".encode(), True),
        (lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "raw-path",
        "raw-nopath",
        "json-path",
        "json-nopath",
        "hyperjson-path",
        "hyperjson-nopath",
    ],
)
@pytest.mark.asyncio
async def test_any(make_async_gen, convert, extract_path):
    matcher = streamson.DepthMatcher("2-2") | streamson.SimpleMatcher('{"users"}')
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    async_out = streamson.extract_async(make_async_gen()(), matcher, handler, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    output = list(Output(e for e in res).generator())

    assert len(output) == 1
    assert output[0] == (
        '{"users"}' if extract_path else None,
        b'["john", "carl", "bob"]',
    )

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}' if extract_path else None,
        [e for e in convert(b'["john", "carl", "bob"]')],
    )
    assert buff_handler.pop_front() is None


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (None, True),
        (None, False),
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: f"X{x.decode()}X".encode(), True),
        (lambda x: f"X{x.decode()}X".encode(), False),
    ],
    ids=[
        "raw-path",
        "raw-nopath",
        "json-path",
        "json-nopath",
        "hyperjson-path",
        "hyperjson-nopath",
    ],
)
@pytest.mark.asyncio
async def test_complex(make_async_gen, convert, extract_path):
    matcher = (streamson.DepthMatcher("2-2") | streamson.SimpleMatcher('{"users"}')) & ~streamson.SimpleMatcher(
        '{"users"}[0]'
    )
    buff_handler = BufferHandler(use_path=extract_path)
    handler = PythonConverterHandler(convert, extract_path) + buff_handler if convert else buff_handler

    async_out = streamson.extract_async(make_async_gen()(), matcher, handler, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    output = list(Output(e for e in res).generator())

    assert len(output) == 1

    assert output[0] == (
        '{"users"}' if extract_path else None,
        b'["john", "carl", "bob"]',
    )

    convert = convert if convert else (lambda x: x)
    assert buff_handler.pop_front() == (
        '{"users"}' if extract_path else None,
        [e for e in convert(b'["john", "carl", "bob"]')],
    )
    assert buff_handler.pop_front() is None
