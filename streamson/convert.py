import typing

from streamson.streamson import Convert, PythonOutput

from .handler import BaseHandler
from .matcher import Matcher


def convert_iter(
    input_gen: typing.Generator[bytes, None, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, BaseHandler]],
) -> typing.Generator[PythonOutput, None, None]:
    """Converts handlers on matched data from a file description
    :param input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination

    :yields: converted data
    """
    convert = Convert()
    for matcher, handler in matchers_and_handlers:
        convert.add_matcher(matcher.inner, handler)

    for item in input_gen:
        for output in convert.process(item):
            yield output

    for output in convert.terminate():
        yield output


def convert_fd(
    input_fd: typing.IO[bytes],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, BaseHandler]],
    buffer_size: int = 1024 * 1024,
) -> typing.Generator[PythonOutput, None, None]:
    """Converts handlers on matched data from a file description
    :param input_fd: input generator
    :param matchers_and_handlers: handler and matchers combination
    :param: buffer_size: how many bytes can be read from a file at once

    :yields: converted data
    """
    convert = Convert()
    for matcher, handler in matchers_and_handlers:
        convert.add_matcher(matcher.inner, handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        for item in convert.process(input_data):
            yield item
        input_data = input_fd.read(buffer_size)

    for output in convert.terminate():
        yield output


async def convert_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, BaseHandler]],
) -> typing.AsyncGenerator[PythonOutput, None]:
    """Convert handlers on matched data from async generator
    :param: input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination

    :yields: input data
    """
    convert = Convert()
    for matcher, handler in matchers_and_handlers:
        convert.add_matcher(matcher.inner, handler)

    async for input_data in input_gen:
        for item in convert.process(input_data):
            yield item

    for output in convert.terminate():
        yield output
