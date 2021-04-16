import pytest

import streamson


@pytest.mark.parametrize(
    "extract_path",
    [True, False],
    ids=[
        "path",
        "nopath",
    ],
)
@pytest.mark.asyncio
async def test_simple(make_async_gen, replace_handler, extract_path):

    matcher = streamson.SimpleMatcher('{"users"}[1]')

    output_data = b""
    async for e in streamson.convert_async(make_async_gen()(), [(matcher, replace_handler)], extract_path):
        output_data += bytes(e.data or [])

    assert output_data == b'{"users": ["john", "***", "bob"]}'
