import io
import json
import typing

import pytest

from streamson.handler import BufferHandler, ReplaceHandler

DATA_JSON = {
    "users": ["john", "carl", "bob"],
    "groups": ["admins", "users"],
}


@pytest.fixture(scope="function")
def make_async_gen():
    def make():
        async def async_in():

            yield b'{"users": '
            yield b'["john", "carl", "bob"'
            yield b"]}"

        return async_in

    return make


@pytest.fixture
def data() -> typing.List[bytes]:
    return [json.dumps(DATA_JSON).encode()]


@pytest.fixture
def io_reader() -> io.BytesIO:
    return io.BytesIO(json.dumps(DATA_JSON).encode())


@pytest.fixture(scope="function")
def buffer_handler():
    return BufferHandler(use_path=True)


@pytest.fixture(scope="function")
def replace_handler():
    def convert_to_stars(path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]):
        return br'"***"'

    return ReplaceHandler(new_data='"***"')
