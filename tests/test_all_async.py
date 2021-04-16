import pytest

import streamson
from streamson.handler import IndenterHandler
from streamson.output import Output


@pytest.mark.asyncio
async def test_basic(make_async_gen):

    async_out = streamson.all_async(make_async_gen()(), [IndenterHandler()])

    res = []
    async for rec in async_out:
        res.append(rec)
    output = list(Output(e for e in res).generator())

    assert len(output) == 1

    assert output[0] == (None, b'{"users":["john","carl","bob"]}')
