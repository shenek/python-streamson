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
async def test_simple(make_async_gen, handler, extract_path):
    hdl, output = handler

    matcher = streamson.SimpleMatcher('{"users"}[]')
    async_out = streamson.trigger_async(make_async_gen()(), [hdl], matcher, extract_path)

    output_data = b""
    async for rec in async_out:
        output_data += rec
    assert output_data == b'{"users": ["john", "carl", "bob"]}'

    assert output == [
        ('{"users"}[0]' if extract_path else None, 0, b'"john"'),
        ('{"users"}[1]' if extract_path else None, 0, b'"carl"'),
        ('{"users"}[2]' if extract_path else None, 0, b'"bob"'),
    ]
