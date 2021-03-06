import typing

from streamson.streamson import BaseHandler, Trigger

from .matcher import Matcher


def trigger_iter(
    input_gen: typing.Generator[bytes, None, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, BaseHandler]],
) -> typing.Generator[bytes, None, None]:
    """Triggers handlers on matched input
    :param input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination

    :yields: input data
    """
    trigger = Trigger()
    for matcher, handler in matchers_and_handlers:
        trigger.add_matcher(matcher.inner, handler)
    for item in input_gen:
        trigger.process(item)
        yield item

    trigger.terminate()


def trigger_fd(
    input_fd: typing.IO[bytes],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, BaseHandler]],
    buffer_size: int = 1024 * 1024,
) -> typing.Generator[bytes, None, None]:
    """Triggers handlers on matched data from a file description
    :param input_fd: input generator
    :param matchers_and_handlers: handler and matchers combination
    :param: buffer_size: how many bytes can be read from a file at once

    :yields: input data
    """
    trigger = Trigger()
    for matcher, handler in matchers_and_handlers:
        trigger.add_matcher(matcher.inner, handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        trigger.process(input_data)
        yield input_data
        input_data = input_fd.read(buffer_size)

    trigger.terminate()


async def trigger_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, BaseHandler]],
):
    """Triggers handlers on matched data from async generator
    :param: input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination

    :yields: input data
    """
    trigger = Trigger()
    for matcher, handler in matchers_and_handlers:
        trigger.add_matcher(matcher.inner, handler)

    async for input_data in input_gen:
        trigger.process(input_data)
        yield input_data

    trigger.terminate()
