import typing

from streamson.streamson import BaseHandler, Trigger

from .matcher import Matcher


def trigger_iter(
    input_gen: typing.Generator[bytes, None, None],
    matcher_handler_combinations: typing.List[typing.Tuple[Matcher, BaseHandler]],
    require_path: bool = True,
) -> typing.Generator[bytes, None, None]:
    """Triggers handlers on matched input
    :param input_gen: input generator
    :param matcher_handler_combinations: list of matcher and handler combination
    :param: require_path: is path required for handlers

    :yields: input data
    """
    trigger = Trigger()
    for matcher, handler in matcher_handler_combinations:
        trigger.add_matcher(matcher.inner, handler)
    for item in input_gen:
        trigger.process(item)
        yield item


def trigger_fd(
    input_fd: typing.IO[bytes],
    matcher_handler_combinations: typing.List[typing.Tuple[Matcher, BaseHandler]],
    buffer_size: int = 1024 * 1024,
    require_path: bool = True,
) -> typing.Generator[bytes, None, None]:
    """Triggers handlers on matched data from a file description
    :param input_fd: input generator
    :param matcher_handler_combinations: list of matcher and handler combination
    :param: buffer_size: how many bytes can be read from a file at once
    :param: require_path: is path required for handlers

    :yields: input data
    """
    trigger = Trigger()
    for matcher, handler in matcher_handler_combinations:
        trigger.add_matcher(matcher.inner, handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        trigger.process(input_data)
        yield input_data
        input_data = input_fd.read(buffer_size)


async def trigger_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matcher_handler_combinations: typing.List[typing.Tuple[Matcher, BaseHandler]],
    require_path: bool = True,
):
    """Triggers handlers on matched data from async generator
    :param: input_gen: input generator
    :param matcher_handler_combinations: list of matcher and handler combination
    :param: require_path: is path required for handlers

    :yields: input data
    """
    trigger = Trigger()
    for matcher, handler in matcher_handler_combinations:
        trigger.add_matcher(matcher.inner, handler)

    async for input_data in input_gen:
        trigger.process(input_data)
        yield input_data
