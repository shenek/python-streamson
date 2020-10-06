import typing

from streamson.streamson import RustMatcher


class Matcher:
    """
    Python Matcher wrapper around actual Rust streamson wrappers.
    """

    def __init__(self, rust_matcher: RustMatcher):
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
        super().__init__(RustMatcher.depth(min_depth, max_depth))


class SimpleMatcher(Matcher):
    def __init__(self, path: str):
        """Simple matcher to use for json matching
        e.g.
        {"user"}[] will match {"user"}[0], {"user"}[1], ...
        {}[0] will match {"user"}[0], {"group"}[0]

        :param: path: which will be used to create a SimpleMatcher
        """
        super().__init__(RustMatcher.simple(path))
