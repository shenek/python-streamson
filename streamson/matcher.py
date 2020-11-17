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
    def __init__(self, depth_str: str):
        """Depth matcher which matches the depth in json.
        :param: depth_str: string in format "min[-max]"
        """
        super().__init__(RustMatcher.depth(depth_str))


class SimpleMatcher(Matcher):
    def __init__(self, path: str):
        """Simple matcher to use for json matching
        e.g.
        {"user"}[] will match {"user"}[0], {"user"}[1], ...
        {}[0] will match {"user"}[0], {"group"}[0]

        :param: path: which will be used to create a SimpleMatcher
        """
        super().__init__(RustMatcher.simple(path))


class AllMatcher(Matcher):
    def __init__(self):
        """Matches all paths"""
        super().__init__(RustMatcher.all())
