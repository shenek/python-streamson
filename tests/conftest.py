import io
import json
import typing

import pytest

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
def handler():
    output: typing.List[typing.Tuple[typing.Optional[str], int, typing.Optional[bytes]]] = []

    def store_to_output(path: typing.Optional[str], matcher_idx: int, data: bytes):
        output.append((path, matcher_idx, data))

    return store_to_output, output


@pytest.fixture(scope="function")
def converter():
    def convert_to_stars(path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]):
        return br'"***"'

    return convert_to_stars
