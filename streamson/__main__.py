import argparse
import sys
import typing

import pkg_resources

import streamson


def convert_parser(root_parser):
    convert = root_parser.add_parser("convert", help="Convert parts of JSON")
    convert.add_argument("-s", "--simple", help="Match by simple match", required=False, action="append")
    convert.add_argument("-d", "--depth", help="Match by depth", required=False, action="append")

    convert.add_argument("-r", "--replace", help="Replaces matched part by given string", required=True)


def extract_parser(root_parser):
    extract = root_parser.add_parser("extract", help="Passes only matched parts of JSON")
    extract.add_argument("-s", "--simple", help="Match by simple match", required=False, action="append")
    extract.add_argument("-d", "--depth", help="Match by depth", required=False, action="append")


def filter_parser(root_parser):
    filter_parser = root_parser.add_parser("filter", help="Removes matched parts of JSON")
    filter_parser.add_argument("-s", "--simple", help="Match by simple match", required=False, action="append")
    filter_parser.add_argument("-d", "--depth", help="Match by depth", required=False, action="append")


def trigger_parser(root_parser):

    trigger_parser = root_parser.add_parser("trigger", help="Triggers command on matched input")

    trigger_parser.add_argument(
        "-f",
        "--file",
        help="Writes matches to file separating records by newline",
        required=False,
        nargs=3,
        metavar=("MATCHER_NAME", "MATCH", "FILE"),
        action="append",
        default=[],
    )

    trigger_parser.add_argument(
        "-p",
        "--print",
        help="Prints matches to stdout separating records by a newline",
        required=False,
        nargs=2,
        metavar=("MATCHER_NAME", "MATCH"),
        action="append",
        default=[],
    )

    trigger_parser.add_argument(
        "-P",
        "--print-with-header",
        help="Prints matches to with header to stdout separating records by a newline",
        required=False,
        nargs=2,
        metavar=("MATCHER_NAME", "MATCH"),
        action="append",
        default=[],
    )


def filter_strategy(options: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    matcher: typing.Optional[streamson.Matcher] = None
    for simple in options.simple:
        if matcher:
            matcher |= streamson.SimpleMatcher(simple)
        else:
            matcher = streamson.SimpleMatcher(simple)

    for depth in options.depth:
        if matcher:
            matcher |= streamson.DepthMatcher(depth)
        else:
            matcher = streamson.DepthMatcher(depth)

    if matcher:
        for output in streamson.filter_iter(input_gen, matcher):
            sys.stdout.write(output)
    else:
        # Just return stdin
        for input_data in input_gen:
            sys.stdout.buffer.write(input_data)


def extract_strategy(options: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    matcher: typing.Optional[streamson.Matcher] = None
    for simple in options.simple:
        if matcher:
            matcher |= streamson.SimpleMatcher(simple)
        else:
            matcher = streamson.SimpleMatcher(simple)

    for depth in options.depth:
        if matcher:
            matcher |= streamson.DepthMatcher(depth)
        else:
            matcher = streamson.DepthMatcher(depth)

    if matcher:
        for _, output in streamson.extract_iter(input_gen, matcher):
            sys.stdout.write(output)


def convert_strategy(options: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    matcher: typing.Optional[streamson.Matcher] = None
    for simple in options.simple:
        if matcher:
            matcher |= streamson.SimpleMatcher(simple)
        else:
            matcher = streamson.SimpleMatcher(simple)

    for depth in options.depth:
        if matcher:
            matcher |= streamson.DepthMatcher(depth)
        else:
            matcher = streamson.DepthMatcher(depth)

    replace_str = options.replace

    def replace(path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]) -> typing.Optional[bytes]:
        return replace_str.encode()

    if matcher:
        for output in streamson.convert_iter(input_gen, [replace], matcher, False):
            sys.stdout.write(output)


def trigger_strategy(options: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    handler_matcher_combinations: typing.List[
        typing.Tuple[
            typing.Callable[[typing.Optional[str], int, typing.Optional[bytes]], typing.Optional[bytes]],
            streamson.Matcher,
        ]
    ] = []

    matcher: streamson.Matcher

    def make_matcher(matcher_name: str, matcher_str: str) -> streamson.Matcher:
        matcher: streamson.Matcher
        if matcher_name == "depth":
            matcher = streamson.DepthMatcher(matcher_str)
            pass
        elif matcher_name == "simple":
            matcher = streamson.SimpleMatcher(matcher_str)
        else:
            raise NotImplementedError()
        return matcher

    for matcher_name, matcher_str in options.print_with_header:

        def handler(
            path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]
        ) -> typing.Optional[bytes]:
            if data:
                sys.stdout.write(f"{path}: {data.decode()}\n")
                sys.stdout.flush()
            return None

        matcher = make_matcher(matcher_name, matcher_str)
        handler_matcher_combinations.append((handler, matcher))

    for matcher_name, matcher_str in options.print:

        def handler(
            path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]
        ) -> typing.Optional[bytes]:
            if data:
                sys.stdout.write(f"{data.decode()}\n")
                sys.stdout.flush()
            return None

        matcher = make_matcher(matcher_name, matcher_str)
        handler_matcher_combinations.append((handler, matcher))

    for matcher_name, matcher_str, file_path in options.file:
        f = open(file_path, "wb")

        def handler(
            path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]
        ) -> typing.Optional[bytes]:
            if data:
                f.write(data + b"\n")
                f.flush()
            return None

        matcher = make_matcher(matcher_name, matcher_str)
        handler_matcher_combinations.append((handler, matcher))

    for output in streamson.trigger_iter(input_gen, handler_matcher_combinations, True):
        pass


def main():
    version = pkg_resources.get_distribution("streamson-python").version

    parser = argparse.ArgumentParser(prog="streamson")
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("-b", "--buffer-size", type=int, default=2 ** 20)

    strategies = parser.add_subparsers(help="strategies", dest="strategy")
    strategies.required = True
    convert_parser(strategies)
    extract_parser(strategies)
    filter_parser(strategies)
    trigger_parser(strategies)

    options = parser.parse_args()

    def input_generator() -> typing.Generator[bytes, None, None]:
        output = sys.stdin.buffer.read(options.buffer_size)
        while len(output) > 0:
            yield output
            output = sys.stdin.buffer.read(options.buffer_size)

    if options.strategy == "filter":
        filter_strategy(options, input_generator())
    elif options.strategy == "extract":
        extract_strategy(options, input_generator())
    elif options.strategy == "convert":
        convert_strategy(options, input_generator())
    elif options.strategy == "trigger":
        trigger_strategy(options, input_generator())


if __name__ == "__main__":
    main()
