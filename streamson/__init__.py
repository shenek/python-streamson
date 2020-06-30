import json
import typing
from array import array

from streamson.streamson import RustMatcher as _RustMatcher
from streamson.streamson import Streamson as _Streamson


class Matcher:
    def __init__(self, rust_matcher: _RustMatcher):
        self.inner = rust_matcher

    def __invert__(self):
        self.inner = self.inner.inv()
        return self

    def __or__(self, other):
        self.inner = self.inner.any(other.inner)
        return self

    def __and__(self, other):
        self.inner = self.inner.all(other.inner)
        return self


class DepthMatcher(Matcher):
    def __init__(self, min_depth: int, max_depth: typing.Optional[int] = None):
        super().__init__(_RustMatcher.depth(min_depth, max_depth))


class SimpleMatcher(Matcher):
    def __init__(self, path: str):
        super().__init__(_RustMatcher.simple(path))


def extract_iter(
    input_gen: typing.Generator[bytes, None, None], matcher: Matcher,
) -> typing.Generator[typing.Tuple[str, typing.Any], None, None]:
    """ Extracts json specified by givem list of simple matches
    :param: input_gen - input generator
    :param: simple_matches - matches to check

    :returns: (string, data) generator
    """
    streamson = _Streamson(matcher.inner)
    for item in input_gen:
        streamson.feed(item)
        res = streamson.pop()
        while res is not None:
            path, data = res
            yield path, json.loads(array("B", data).tobytes())
            res = streamson.pop()
