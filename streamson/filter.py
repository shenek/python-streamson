import typing

from streamson.streamson import Filter, PythonOutput

from .handler import BaseHandler
from .matcher import Matcher


def filter_iter(
    input_gen: typing.Generator[bytes, None, None],
    matcher: Matcher,
    handler: typing.Optional[BaseHandler] = None,
) -> typing.Generator[PythonOutput, None, None]:
    """Filters json parts from generator specified by given matcher
    :param: input_gen: input generator
    :param: matcher: used matcher
    :param: handler: function used to convert raw data

    :yields: filtered data
    """
    filter_strategy = Filter()
    filter_strategy.add_matcher(matcher.inner, handler)
    for item in input_gen:
        for item in filter_strategy.process(item):
            yield item


def filter_fd(
    input_fd: typing.IO[bytes],
    matcher: Matcher,
    handler: typing.Optional[BaseHandler] = None,
    buffer_size: int = 1024 * 1024,
) -> typing.Generator[PythonOutput, None, None]:
    """Filters json parts from input file specified by given matcher
    :param: input_fd: input fd
    :param: matcher: used matcher
    :param: handler: function used to convert raw data
    :param: buffer_size: how many bytes can be read from a file at once

    :yields: filtered data
    """
    filter_strategy = Filter()
    filter_strategy.add_matcher(matcher.inner, handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        for item in filter_strategy.process(input_data):
            yield item
        input_data = input_fd.read(buffer_size)


async def filter_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matcher: Matcher,
    handler: typing.Optional[BaseHandler] = None,
):
    """Filters json parts from given async generator specified by given matcher
    :param: input_gen: input generator
    :param: matcher: used matcher
    :param: handler: function used to convert raw data

    :yields: filtered data
    """
    filter_strategy = Filter()
    filter_strategy.add_matcher(matcher.inner, handler)

    async for input_data in input_gen:
        for item in filter_strategy.process(input_data):
            yield item
