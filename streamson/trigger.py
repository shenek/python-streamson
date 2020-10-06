import typing

from streamson.streamson import PythonHandler, Trigger

from .matcher import Matcher


def trigger_iter(
    input_gen: typing.Generator[bytes, None, None],
    handlers: typing.List[typing.Callable[[typing.Optional[str], int, bytes], None]],
    matcher: Matcher,
    require_path: bool = True,
) -> typing.Generator[bytes, None, None]:
    """Triggers handlers on matched input
    :param input_gen: input generator
    :param handlers: list of handlers which should be called on match
    :param matcher: used matcher
    :param: require_path: is path required for handlers

    :yields: input data
    """
    trigger = Trigger()
    trigger.add_matcher(matcher.inner, [PythonHandler(handler, require_path) for handler in handlers])
    for item in input_gen:
        trigger.process(item)
        yield item


def trigger_fd(
    input_fd: typing.IO[bytes],
    handlers: typing.List[typing.Callable[[typing.Optional[str], int, bytes], None]],
    matcher: Matcher,
    buffer_size: int = 1024 * 1024,
    require_path: bool = True,
) -> typing.Generator[bytes, None, None]:
    """Triggers handlers on matched data from a file description
    :param input_fd: input generator
    :param handlers: list of handlers which should be called on match
    :param matcher: used matcher
    :param: buffer_size: how many bytes can be read from a file at once
    :param: require_path: is path required for handlers

    :yields: input data
    """
    trigger = Trigger()
    trigger.add_matcher(matcher.inner, [PythonHandler(handler, require_path) for handler in handlers])

    input_data = input_fd.read(buffer_size)

    while input_data:
        trigger.process(input_data)
        yield input_data
        input_data = input_fd.read(buffer_size)


async def trigger_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    handlers: typing.List[typing.Callable[[typing.Optional[str], int, bytes], None]],
    matcher: Matcher,
    require_path: bool = True,
):
    """Triggers handlers on matched data from async generator
    :param: input_gen: input generator
    :param handlers: list of handlers which should be called on match
    :param: matcher: used matcher
    :param: require_path: is path required for handlers

    :yields: input data
    """
    trigger = Trigger()
    trigger.add_matcher(matcher.inner, [PythonHandler(handler, require_path) for handler in handlers])

    async for input_data in input_gen:
        trigger.process(input_data)
        yield input_data
