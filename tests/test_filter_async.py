import pytest
import streamson
from streamson.handler import BufferHandler
from streamson.output import Output


@pytest.mark.asyncio
async def test_simple(make_async_gen, buffer_handler):
    matcher = streamson.SimpleMatcher('{"users"}[]')
    async_out = streamson.filter_async(make_async_gen()(), matcher, buffer_handler)

    res = []
    async for rec in async_out:
        res.append(rec)
    output = list(Output(e for e in res).generator())

    assert len(output) == 1

    assert output[0] == (None, b'{"users": []}')
