import argparse
import collections
import json
import re
import sys
import typing

import pkg_resources

import streamson


def convert_parser(root_parser):
    convert = root_parser.add_parser("convert", help="Convert parts of JSON")
    convert.add_argument("-s", "--simple", help="Match by simple match", required=False, action="append")
    convert.add_argument("-d", "--depth", help="Match by depth", required=False, action="append")
    convert.add_argument("-x", "--regex", help="Match by regex", required=False, action="append")

    action = convert.add_mutually_exclusive_group(required=True)
    action.add_argument("-r", "--replace", help="Replaces matched part by given string")
    action.add_argument("-o", "--shorten", help="Shortens matched data", nargs=2, metavar=("MAX_COUNT", "TERMINATOR"))
    action.add_argument("-u", "--unstringify", help="Unstringifies matched data", action="store_true")


def extract_parser(root_parser):
    extract = root_parser.add_parser("extract", help="Passes only matched parts of JSON")
    extract.add_argument("-s", "--simple", help="Match by simple match", required=False, action="append")
    extract.add_argument("-d", "--depth", help="Match by depth", required=False, action="append")
    extract.add_argument("-x", "--regex", help="Match by regex", required=False, action="append")
    extract.add_argument("-b", "--before", help="Will be printed before matched outputs", required=False, default="")
    extract.add_argument("-a", "--after", help="Will be printed after matched outputs", required=False, default="")
    extract.add_argument(
        "-S",
        "--separator",
        help="Will be printed to separate matched outputs",
        required=False,
        default="",
    )


def filter_parser(root_parser):
    filter_parser = root_parser.add_parser("filter", help="Removes matched parts of JSON")
    filter_parser.add_argument("-s", "--simple", help="Match by simple match", required=False, action="append")
    filter_parser.add_argument("-d", "--depth", help="Match by depth", required=False, action="append")
    filter_parser.add_argument("-x", "--regex", help="Match by regex", required=False, action="append")


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

    trigger_parser.add_argument(
        "-s",
        "--struct",
        help="Goes through a json and prints JSON structure at the end of processing.",
        action="store_true",
    )


def filter_strategy(options: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    matcher: typing.Optional[streamson.Matcher] = None
    for simple in options.simple or []:
        if matcher:
            matcher |= streamson.SimpleMatcher(simple)
        else:
            matcher = streamson.SimpleMatcher(simple)

    for depth in options.depth or []:
        if matcher:
            matcher |= streamson.DepthMatcher(depth)
        else:
            matcher = streamson.DepthMatcher(depth)

    for regex in options.regex or []:
        if matcher:
            matcher |= streamson.RegexMatcher(regex)
        else:
            matcher = streamson.RegexMatcher(regex)

    if matcher:
        for output in streamson.filter_iter(input_gen, matcher):
            sys.stdout.write(output)
    else:
        # Just return stdin
        for input_data in input_gen:
            sys.stdout.buffer.write(input_data)


def extract_strategy(options: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    matcher: typing.Optional[streamson.Matcher] = None
    for simple in options.simple or []:
        if matcher:
            matcher |= streamson.SimpleMatcher(simple)
        else:
            matcher = streamson.SimpleMatcher(simple)

    for depth in options.depth or []:
        if matcher:
            matcher |= streamson.DepthMatcher(depth)
        else:
            matcher = streamson.DepthMatcher(depth)

    for regex in options.regex or []:
        if matcher:
            matcher |= streamson.RegexMatcher(regex)
        else:
            matcher = streamson.RegexMatcher(regex)

    if matcher:
        sys.stdout.write(options.before)
        first = True
        for _, output in streamson.extract_iter(input_gen, matcher):
            if not first:
                sys.stdout.write(options.separator)
            else:
                first = False
            sys.stdout.write(output)
        sys.stdout.write(options.after)


def convert_strategy(options: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    matcher: typing.Optional[streamson.Matcher] = None
    for simple in options.simple or []:
        if matcher:
            matcher |= streamson.SimpleMatcher(simple)
        else:
            matcher = streamson.SimpleMatcher(simple)

    for depth in options.depth or []:
        if matcher:
            matcher |= streamson.DepthMatcher(depth)
        else:
            matcher = streamson.DepthMatcher(depth)

    for regex in options.regex or []:
        if matcher:
            matcher |= streamson.RegexMatcher(regex)
        else:
            matcher = streamson.RegexMatcher(regex)

    if options.shorten:

        def shorten(
            path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]
        ) -> typing.Optional[bytes]:
            length, end = options.shorten
            if data:
                return bytes(bytearray(data[: int(length) + 1])) + end.encode()

            return None

        converter = shorten

    elif options.replace:

        def replace(
            path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]
        ) -> typing.Optional[bytes]:
            return options.replace.encode()

        converter = replace

    elif options.unstringify:

        def unstringify(
            path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]
        ) -> typing.Optional[bytes]:
            if data:
                try:
                    return json.dumps(json.loads(json.loads(bytes(bytearray(data)).decode()))).encode()
                except Exception:
                    return data

            return data

        converter = unstringify

    if matcher:
        for output in streamson.convert_iter(input_gen, [converter], matcher, False):
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
        elif matcher_name == "regex":
            matcher = streamson.RegexMatcher(matcher_str)
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

    if options.struct:
        counter: typing.Counter[str] = collections.Counter()

        def handler(
            path: typing.Optional[str], matcher_idx: int, data: typing.Optional[bytes]
        ) -> typing.Optional[bytes]:

            key = "<root>" if not path else re.sub(r"\[[0-9\-,]*\]", "[]", path)
            counter[key] += 1
            return None

        matcher = streamson.AllMatcher()
        handler_matcher_combinations.append((handler, matcher))

    for output in streamson.trigger_iter(input_gen, handler_matcher_combinations, True):
        pass

    if options.struct:
        print("JSON structure:")
        for key in sorted(counter):
            print(f"  {key}: {counter[key]}")


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
