import pytest

import streamson


@pytest.mark.asyncio
async def test_simple(make_async_gen, handler):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    async_out = streamson.filter_async(make_async_gen()(), matcher)

    output_data = ""
    async for rec in async_out:
        output_data += rec

    assert output_data == '{"users": []}'
