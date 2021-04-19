import pytest

import streamson


@pytest.mark.asyncio
async def test_simple(make_async_gen, replace_handler):

    matcher = streamson.SimpleMatcher('{"users"}[1]')

    output_data = b""
    async for e in streamson.convert_async(make_async_gen()(), [(matcher, replace_handler)]):
        if e is not None and e[1] is not None:
            output_data += e[1]

    assert output_data == b'{"users": ["john", "***", "bob"]}'
