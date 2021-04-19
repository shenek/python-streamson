import typing

from streamson.output import PythonOutput
from streamson.streamson import Filter

from .handler import BaseHandler
from .matcher import Matcher


def filter_iter(
    input_gen: typing.Generator[bytes, None, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, typing.Optional[BaseHandler]]],
) -> typing.Generator[PythonOutput, None, None]:
    """Filters json parts from generator specified by given matcher
    :param: input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination

    :yields: filtered data
    """
    filter_strategy = Filter()
    for matcher, handler in matchers_and_handlers:
        filter_strategy.add_matcher(matcher.inner, handler)
    for item in input_gen:
        for filter_item in filter_strategy.process(item):
            yield filter_item

    for output in filter_strategy.terminate():
        yield output


def filter_fd(
    input_fd: typing.IO[bytes],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, typing.Optional[BaseHandler]]],
    buffer_size: int = 1024 * 1024,
) -> typing.Generator[PythonOutput, None, None]:
    """Filters json parts from input file specified by given matcher
    :param: input_fd: input fd
    :param matchers_and_handlers: handler and matchers combination
    :param: buffer_size: how many bytes can be read from a file at once

    :yields: filtered data
    """
    filter_strategy = Filter()
    for matcher, handler in matchers_and_handlers:
        filter_strategy.add_matcher(matcher.inner, handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        for item in filter_strategy.process(input_data):
            yield item
        input_data = input_fd.read(buffer_size)

    for output in filter_strategy.terminate():
        yield output


async def filter_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, typing.Optional[BaseHandler]]],
):
    """Filters json parts from given async generator specified by given matcher
    :param: input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination

    :yields: filtered data
    """
    filter_strategy = Filter()
    for matcher, handler in matchers_and_handlers:
        filter_strategy.add_matcher(matcher.inner, handler)

    async for input_data in input_gen:
        for item in filter_strategy.process(input_data):
            yield item

    for output in filter_strategy.terminate():
        yield output
