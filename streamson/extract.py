import typing

from streamson.streamson import Extract

from .matcher import Matcher


def extract_iter(
    input_gen: typing.Generator[bytes, None, None],
    matcher: Matcher,
    convert: typing.Callable[[str], typing.Any] = lambda x: x,
    require_path: bool = True,
) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
    """Extracts json from generator specified by given simple matcher
    :param: input_gen: input generator
    :param: matcher: used matcher
    :param: convert: function used to convert raw data
    :param: require_path: is path required in output stream

    :yields: path and converted data
    """
    extract = Extract(matcher.inner, require_path)
    for item in input_gen:
        for path, data in extract.process(item):
            yield path, convert(data)


def extract_fd(
    input_fd: typing.IO[bytes],
    matcher: Matcher,
    buffer_size: int = 1024 * 1024,
    convert: typing.Callable[[str], typing.Any] = lambda x: x,
    require_path: bool = True,
) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
    """Extracts json from input file specified by given simple matcher
    :param: input_fd: input fd
    :param: buffer_size: how many bytes can be read from a file at once
    :param: matcher: used matcher
    :param: convert: function used to convert raw data
    :param: require_path: is path required in output stream

    :yields: path and converted data
    """
    extract = Extract(matcher.inner, require_path)
    input_data = input_fd.read(buffer_size)

    while input_data:
        for path, data in extract.process(input_data):
            yield path, convert(data)
        input_data = input_fd.read(buffer_size)


async def extract_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matcher: Matcher,
    convert: typing.Callable[[str], typing.Any] = lambda x: x,
    require_path: bool = True,
):
    """Extracts json from given async generator specified by given simple matcher
    :param: input_gen: input generator
    :param: matcher: used matcher
    :param: convert: function used to convert raw data
    :param: require_path: is path required in output stream

    :yields: path and converted data
    """
    extract = Extract(matcher.inner, require_path)
    async for input_data in input_gen:
        for path, data in extract.process(input_data):
            yield path, convert(data)
