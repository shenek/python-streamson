import pytest

import streamson
from streamson.handler import BufferHandler


@pytest.mark.parametrize(
    "extract_path",
    [True, False],
    ids=[
        "path",
        "nopath",
    ],
)
@pytest.mark.asyncio
async def test_simple(make_async_gen, extract_path):
    handler = BufferHandler(use_path=extract_path)
    matcher = streamson.SimpleMatcher('{"users"}[]')
    async_out = streamson.trigger_async(make_async_gen()(), [(matcher, handler)], extract_path)

    output_data = b""
    async for rec in async_out:
        output_data += rec
    assert output_data == b'{"users": ["john", "carl", "bob"]}'

    assert handler.pop_front() == ('{"users"}[0]' if extract_path else None, [e for e in b'"john"'])
    assert handler.pop_front() == ('{"users"}[1]' if extract_path else None, [e for e in b'"carl"'])
    assert handler.pop_front() == ('{"users"}[2]' if extract_path else None, [e for e in b'"bob"'])
