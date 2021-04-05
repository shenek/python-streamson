import typing

from streamson.streamson import Convert, PythonOutput

from .handler import BaseHandler
from .matcher import Matcher


def convert_iter(
    input_gen: typing.Generator[bytes, None, None],
    handler: BaseHandler,
    matcher: Matcher,
    require_path: bool = True,
) -> typing.Generator[PythonOutput, None, None]:
    """Converts handlers on matched data from a file description
    :param input_gen: input generator
    :param handler: handler which should be called on match
    :param matcher: used matcher
    :param: require_path: is path required for handlers

    :yields: converted data
    """
    convert = Convert()
    convert.add_matcher(matcher.inner, handler)
    for item in input_gen:
        for output in convert.process(item):
            yield output


def convert_fd(
    input_fd: typing.IO[bytes],
    handler: BaseHandler,
    matcher: Matcher,
    buffer_size: int = 1024 * 1024,
    require_path: bool = True,
) -> typing.Generator[PythonOutput, None, None]:
    """Converts handlers on matched data from a file description
    :param input_fd: input generator
    :param handler: handler which should be called on match
    :param matcher: used matcher
    :param: buffer_size: how many bytes can be read from a file at once
    :param: require_path: is path required for handlers

    :yields: converted data
    """
    convert = Convert()
    convert.add_matcher(matcher.inner, handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        for item in convert.process(input_data):
            yield item
        input_data = input_fd.read(buffer_size)


async def convert_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    handler: BaseHandler,
    matcher: Matcher,
    require_path: bool = True,
) -> typing.AsyncGenerator[PythonOutput, None]:
    """Convert handlers on matched data from async generator
    :param: input_gen: input generator
    :param handler: handler which should be called on match
    :param: matcher: used matcher
    :param: require_path: is path required for handlers

    :yields: input data
    """
    convert = Convert()
    convert.add_matcher(matcher.inner, handler)

    async for input_data in input_gen:
        for item in convert.process(input_data):
            yield item
