import typing

from streamson.streamson import Filter

from .matcher import Matcher


def filter_iter(
    input_gen: typing.Generator[bytes, None, None],
    matcher: Matcher,
) -> typing.Generator[str, None, None]:
    """Filters json parts from generator specified by given matcher
    :param: input_gen: input generator
    :param: matcher: used matcher

    :yields: filtered data
    """
    filter_strategy = Filter()
    filter_strategy.add_matcher(matcher.inner)
    for item in input_gen:
        yield filter_strategy.process(item)


def filter_fd(
    input_fd: typing.IO[bytes],
    matcher: Matcher,
    buffer_size: int = 1024 * 1024,
) -> typing.Generator[str, None, None]:
    """Filters json parts from input file specified by given matcher
    :param: input_fd: input fd
    :param: matcher: used matcher
    :param: buffer_size: how many bytes can be read from a file at once

    :yields: filtered data
    """
    filter_strategy = Filter()
    filter_strategy.add_matcher(matcher.inner)

    input_data = input_fd.read(buffer_size)

    while input_data:
        yield filter_strategy.process(input_data)
        input_data = input_fd.read(buffer_size)


async def filter_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matcher: Matcher,
):
    """Filters json parts from given async generator specified by given matcher
    :param: input_gen: input generator
    :param: matcher: used matcher

    :yields: filtered data
    """
    filter_strategy = Filter()
    filter_strategy.add_matcher(matcher.inner)

    async for input_data in input_gen:
        yield filter_strategy.process(input_data)
