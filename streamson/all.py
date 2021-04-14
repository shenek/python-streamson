import typing

from streamson.streamson import All, PythonOutput

from .handler import BaseHandler


def all_iter(
    input_gen: typing.Generator[bytes, None, None],
    handler: BaseHandler,
    convert: bool = True,
) -> typing.Generator[PythonOutput, None, None]:
    """Applies handler to all json parts from generator
    :param: input_gen: input generator
    :param: handler: function used to convert/process raw data
    :param: convert: should handler be used to convert the output

    :yields: filtered data
    """
    all_strategy = All(convert)
    all_strategy.add_handler(handler)
    for item in input_gen:
        for item in all_strategy.process(item):
            yield item


def all_fd(
    input_fd: typing.IO[bytes],
    handler: BaseHandler,
    convert: bool = True,
    buffer_size: int = 1024 * 1024,
) -> typing.Generator[PythonOutput, None, None]:
    """Applies handler to all json parts from input file
    :param: input_fd: input fd
    :param: handler: function used to convert raw data
    :param: convert: should handler be used to convert the output
    :param: buffer_size: how many bytes can be read from a file at once

    :yields: filtered data
    """
    all_strategy = All(convert)
    all_strategy.add_handler(handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        for item in all_strategy.process(input_data):
            yield item
        input_data = input_fd.read(buffer_size)


async def all_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    handler: BaseHandler,
    convert: bool = True,
):
    """Applies handler to all json parts from async generator
    :param: input_gen: input generator
    :param: handler: function used to convert raw data
    :param: convert: should handler be used to convert the output

    :yields: filtered data
    """
    all_strategy = All(convert)
    all_strategy.add_handler(handler)

    async for input_data in input_gen:
        for item in all_strategy.process(input_data):
            yield item
