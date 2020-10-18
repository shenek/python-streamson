import json

import hyperjson
import pytest

import streamson


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: json.dumps(x), True),
        (lambda x: json.dumps(x), False),
        (lambda x: hyperjson.dumps(x), True),
        (lambda x: hyperjson.dumps(x), False),
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
    async_out = streamson.extract_async(make_async_gen()(), matcher, convert, extract_path)

    res = []

    async for rec in async_out:
        res.append(rec)

    assert len(res) == 3

    assert res[0] == ('{"users"}[0]' if extract_path else None, convert('"john"'))
    assert res[1] == ('{"users"}[1]' if extract_path else None, convert('"carl"'))
    assert res[2] == ('{"users"}[2]' if extract_path else None, convert('"bob"'))


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: json.dumps(x), True),
        (lambda x: json.dumps(x), False),
        (lambda x: hyperjson.dumps(x), True),
        (lambda x: hyperjson.dumps(x), False),
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

    async_out = streamson.extract_async(make_async_gen()(), matcher, convert, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    assert len(res) == 1

    assert res[0] == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )

    matcher = streamson.DepthMatcher("0-1")
    async_out = streamson.extract_async(make_async_gen()(), matcher, convert, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    assert len(res) == 1
    assert res[0] == (
        "" if extract_path else None,
        convert('{"users": ["john", "carl", "bob"]}'),
    )


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: json.dumps(x), True),
        (lambda x: json.dumps(x), False),
        (lambda x: hyperjson.dumps(x), True),
        (lambda x: hyperjson.dumps(x), False),
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
    async_out = streamson.extract_async(make_async_gen()(), matcher, convert, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    assert len(res) == 1

    assert res[0] == (
        "" if extract_path else None,
        convert('{"users": ["john", "carl", "bob"]}'),
    )


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: json.dumps(x), True),
        (lambda x: json.dumps(x), False),
        (lambda x: hyperjson.dumps(x), True),
        (lambda x: hyperjson.dumps(x), False),
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

    async_out = streamson.extract_async(make_async_gen()(), matcher, convert, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    assert len(res) == 1

    assert res[0] == ('{"users"}[1]' if extract_path else None, convert('"carl"'))


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: json.dumps(x), True),
        (lambda x: json.dumps(x), False),
        (lambda x: hyperjson.dumps(x), True),
        (lambda x: hyperjson.dumps(x), False),
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

    async_out = streamson.extract_async(make_async_gen()(), matcher, convert, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    assert len(res) == 1
    assert res[0] == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )


@pytest.mark.parametrize(
    "convert,extract_path",
    [
        (lambda x: x, True),
        (lambda x: x, False),
        (lambda x: json.dumps(x), True),
        (lambda x: json.dumps(x), False),
        (lambda x: hyperjson.dumps(x), True),
        (lambda x: hyperjson.dumps(x), False),
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

    async_out = streamson.extract_async(make_async_gen()(), matcher, convert, extract_path)

    res = []
    async for rec in async_out:
        res.append(rec)

    assert len(res) == 1

    assert res[0] == (
        '{"users"}' if extract_path else None,
        convert('["john", "carl", "bob"]'),
    )
