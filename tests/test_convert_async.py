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
async def test_simple(make_async_gen, converter, extract_path):

    matcher = streamson.SimpleMatcher('{"users"}[1]')

    output_data = ""
    async for e in streamson.convert_async(make_async_gen()(), [converter], matcher, extract_path):
        output_data += e

    assert output_data == '{"users": ["john", "***", "bob"]}'
