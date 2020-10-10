import typing

from streamson.streamson import Convert, PythonConverter

from .matcher import Matcher


def convert_iter(
    input_gen: typing.Generator[bytes, None, None],
    handlers: typing.List[typing.Callable[[typing.Optional[str], int, typing.Optional[bytes]], typing.Optional[bytes]]],
    matcher: Matcher,
    require_path: bool = True,
) -> typing.Generator[str, None, None]:
    """Converts handlers on matched data from a file description
    :param input_gen: input generator
    :param handlers: list of handlers which should be called on match
    :param matcher: used matcher
    :param: require_path: is path required for handlers

    :yields: converted data
    """
    convert = Convert()
    convert.add_matcher(matcher.inner, [PythonConverter(handler, require_path) for handler in handlers])
    for item in input_gen:
        for output in convert.process(item):
            yield output


def convert_fd(
    input_fd: typing.IO[bytes],
    handlers: typing.List[typing.Callable[[typing.Optional[str], int, typing.Optional[bytes]], typing.Optional[bytes]]],
    matcher: Matcher,
    buffer_size: int = 1024 * 1024,
    require_path: bool = True,
) -> typing.Generator[str, None, None]:
    """Converts handlers on matched data from a file description
    :param input_fd: input generator
    :param handlers: list of handlers which should be called on match
    :param matcher: used matcher
    :param: buffer_size: how many bytes can be read from a file at once
    :param: require_path: is path required for handlers

    :yields: converted data
    """
    convert = Convert()
    convert.add_matcher(matcher.inner, [PythonConverter(handler, require_path) for handler in handlers])

    input_data = input_fd.read(buffer_size)

    while input_data:
        for item in convert.process(input_data):
            yield item
        input_data = input_fd.read(buffer_size)


async def convert_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    handlers: typing.List[typing.Callable[[typing.Optional[str], int, typing.Optional[bytes]], typing.Optional[bytes]]],
    matcher: Matcher,
    require_path: bool = True,
) -> typing.AsyncGenerator[str, None]:
    """Convert handlers on matched data from async generator
    :param: input_gen: input generator
    :param handlers: list of handlers which should be called on match
    :param: matcher: used matcher
    :param: require_path: is path required for handlers

    :yields: input data
    """
    convert = Convert()
    convert.add_matcher(matcher.inner, [PythonConverter(handler, require_path) for handler in handlers])

    async for input_data in input_gen:
        for item in convert.process(input_data):
            yield item
