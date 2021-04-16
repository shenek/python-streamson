import typing

from streamson.streamson import Extract, PythonOutput

from .handler import BaseHandler
from .matcher import Matcher


def extract_iter(
    input_gen: typing.Generator[bytes, None, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, typing.Optional[BaseHandler]]],
    require_path: bool = True,
) -> typing.Generator[PythonOutput, None, None]:
    """Extracts json from generator specified by given matcher
    :param: input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination
    :param: require_path: is path required in output stream

    :yields: path and converted data
    """
    extract = Extract(require_path)
    for matcher, handler in matchers_and_handlers:
        extract.add_matcher(matcher.inner, handler)
    for item in input_gen:
        for output in extract.process(item):
            yield output

    for output in extract.terminate():
        yield output


def extract_fd(
    input_fd: typing.IO[bytes],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, typing.Optional[BaseHandler]]],
    buffer_size: int = 1024 * 1024,
    require_path: bool = True,
) -> typing.Generator[PythonOutput, None, None]:
    """Extracts json from input file specified by given matcher
    :param: input_fd: input fd
    :param matchers_and_handlers: handler and matchers combination
    :param: buffer_size: how many bytes can be read from a file at once
    :param: require_path: is path required in output stream

    :yields: path and converted data
    """
    extract = Extract(require_path)
    for matcher, handler in matchers_and_handlers:
        extract.add_matcher(matcher.inner, handler)

    input_data = input_fd.read(buffer_size)

    while input_data:
        for output in extract.process(input_data):
            yield output
        input_data = input_fd.read(buffer_size)

    for output in extract.terminate():
        yield output


async def extract_async(
    input_gen: typing.AsyncGenerator[bytes, None],
    matchers_and_handlers: typing.List[typing.Tuple[Matcher, typing.Optional[BaseHandler]]],
    require_path: bool = True,
):
    """Extracts json from given async generator specified by given matcher
    :param: input_gen: input generator
    :param matchers_and_handlers: handler and matchers combination
    :param: require_path: is path required in output stream

    :yields: path and converted data
    """
    extract = Extract(require_path)
    for matcher, handler in matchers_and_handlers:
        extract.add_matcher(matcher.inner, handler)

    async for input_data in input_gen:
        for output in extract.process(input_data):
            yield output

    for output in extract.terminate():
        yield output
