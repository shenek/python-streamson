import typing

from streamson.streamson import RustMatcher as _RustMatcher
from streamson.streamson import Streamson as _Streamson


class Matcher:
    """
    Python Matcher wrapper around actual Rust streamson wrappers.
    """

    def __init__(self, rust_matcher: _RustMatcher):
        self.inner = rust_matcher

    def __invert__(self):
        return Matcher(~self.inner)

    def __or__(self, other):
        return Matcher(self.inner | other.inner)

    def __and__(self, other):
        return Matcher(self.inner & other.inner)


class DepthMatcher(Matcher):
    def __init__(
        self,
        min_depth: int,
        max_depth: typing.Optional[int] = None,
    ):
        """Depth matcher which matches the depth in json.
        :param: min_depth: minimal matched depth
        :param: max_depth: maximal matched depth (optinal if not set it will match all higher)
        """
        super().__init__(_RustMatcher.depth(min_depth, max_depth))


class SimpleMatcher(Matcher):
    def __init__(self, path: str):
        """Simple matcher to use for json matching
        e.g.
        {"user"}[] will match {"user"}[0], {"user"}[1], ...
        {}[0] will match {"user"}[0], {"group"}[0]

        :param: path: which will be used to create a SimpleMatcher
        """
        super().__init__(_RustMatcher.simple(path))


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
    streamson = _Streamson(matcher.inner, require_path)
    for item in input_gen:
        streamson.feed(item)
        res = streamson.pop()
        while res is not None:
            path, data = res
            yield path, convert(data)
            res = streamson.pop()


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
    streamson = _Streamson(matcher.inner, require_path)
    input_data = input_fd.read(buffer_size)

    while input_data:
        streamson.feed(input_data)
        res = streamson.pop()
        while res is not None:
            path, data = res
            yield path, convert(data)
            res = streamson.pop()

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
    streamson = _Streamson(matcher.inner, require_path)
    async for input_data in input_gen:
        streamson.feed(input_data)

        res = streamson.pop()
        while res is not None:
            path, data = res
            yield path, convert(data)
            res = streamson.pop()
