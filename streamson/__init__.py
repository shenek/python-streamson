try:
    import hyperjson

    json_module = hyperjson
except ImportError:
    import json

    json_module = json

import typing
from array import array

from streamson.streamson import RustMatcher as _RustMatcher
from streamson.streamson import Streamson as _Streamson


class Matcher:
    def __init__(self, rust_matcher: _RustMatcher):
        self.inner = rust_matcher

    def __invert__(self):
        return Matcher(~self.inner)

    def __or__(self, other):
        return Matcher(self.inner | other.inner)

    def __and__(self, other):
        return Matcher(self.inner & other.inner)


class DepthMatcher(Matcher):
    def __init__(self, min_depth: int, max_depth: typing.Optional[int] = None):
        """ Depth matcher which matches the depth in json.
        :param: min_depth: minimal matched depth
        :param: max_depth: maximal matched depth (optinal if not set it will match all higher)
        """
        super().__init__(_RustMatcher.depth(min_depth, max_depth))


class SimpleMatcher(Matcher):
    def __init__(self, path: str):
        """ Simple matcher to use for json matching
        e.g.
        {"user"}[] will match {"user"}[0], {"user"}[1], ...
        {}[0] will match {"user"}[0], {"group"}[0]

        """
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
            yield path, json_module.loads(array("B", data).tobytes())
            res = streamson.pop()
