import argparse
import sys
import typing
from enum import Enum, auto

import pkg_resources

import streamson


class Matcher(Enum):
    SIMPLE = auto()
    DEPTH = auto()
    REGEX = auto()

    @staticmethod
    def from_name(name: str) -> "Matcher":
        if name == "s" or name == "simple":
            return Matcher.SIMPLE
        if name == "d" or name == "depth":
            return Matcher.DEPTH
        if name == "x" or name == "regex":
            return Matcher.REGEX

        raise RuntimeError(f"Unknown matcher name '{name}'")

    def instance(self, definition) -> streamson.Matcher:
        if self == Matcher.SIMPLE:
            return streamson.matcher.SimpleMatcher(definition)
        elif self == Matcher.DEPTH:
            return streamson.matcher.DepthMatcher(definition)
        elif self == Matcher.REGEX:
            return streamson.matcher.RegexMatcher(definition)

        raise NotImplementedError()


class Handler(Enum):
    ANALYSER = auto()
    FILE = auto()
    INDENTER = auto()
    REGEX = auto()
    REPLACE = auto()
    SHORTEN = auto()
    UNSTRINGIFY = auto()

    @staticmethod
    def from_name(name: str) -> "Handler":
        if name == "a" or name == "analyser":
            return Handler.ANALYSER
        elif name == "f" or name == "file":
            return Handler.FILE
        elif name == "d" or name == "indenter":
            return Handler.INDENTER
        elif name == "x" or name == "regex":
            return Handler.REGEX
        elif name == "r" or name == "replace":
            return Handler.REPLACE
        elif name == "s" or name == "shorten":
            return Handler.SHORTEN
        elif name == "u" or name == "unstringify":
            return Handler.UNSTRINGIFY

        raise RuntimeError(f"Unknown matcher name '{name}'")

    def instance(self, definition: typing.Optional[str] = None, *options: str) -> streamson.handler.BaseHandler:
        if self == Handler.ANALYSER:
            if definition or options:
                raise ValueError("Analyser handler has no definition nor options")
            return streamson.handler.AnalyserHandler()
        elif self == Handler.FILE:
            if not definition:
                raise ValueError("File handler requires definition (path) as an argument")
            if len(options) == 1:
                write_path = options[0].lower() == "true"
            else:
                write_path = False
            return streamson.handler.FileHandler(definition, write_path)
        elif self == Handler.INDENTER:
            if options:
                raise ValueError("Indenter handler has no options")
            return streamson.handler.IndenterHandler(definition)
        elif self == Handler.REGEX:
            if options:
                raise ValueError("Regex handler has no options")
            return streamson.handler.RegexHandler([definition])
        elif self == Handler.REPLACE:
            if options:
                raise ValueError("Replace handler has no options")
            return streamson.handler.ReplaceHandler(definition)
        elif self == Handler.SHORTEN:
            if options:
                raise ValueError("Shorten handler has no options")
            if not definition:
                raise ValueError("Shorten handler: length option is required")
            splitted = definition.split(",", 1)
            if len(splitted) != 2:
                raise ValueError("Shorten handler has wrong definition (size,terminator)")
            try:
                size = int(splitted[0])
            except ValueError:
                raise ValueError("Shorten handler has wrong definition (size,terminator)")
            return streamson.handler.ShortenHandler(size, splitted[1])
        elif self == Handler.UNSTRINGIFY:
            if definition or options:
                raise ValueError("Unstringify handler has no definition nor options")
            return streamson.handler.UnstringifyHandler()

        raise NotImplementedError()


class Strategy(Enum):
    CONVERT = auto()
    FILTER = auto()
    EXTRACT = auto()
    TRIGGER = auto()

    def available_handlers(self) -> typing.Tuple[Handler, ...]:
        if self == Strategy.CONVERT:
            return (Handler.FILE, Handler.REGEX, Handler.REPLACE, Handler.SHORTEN, Handler.UNSTRINGIFY)
        if self == Strategy.FILTER:
            return (Handler.FILE, Handler.REGEX, Handler.SHORTEN, Handler.UNSTRINGIFY)
        if self == Strategy.EXTRACT:
            return (Handler.FILE, Handler.REGEX, Handler.SHORTEN, Handler.UNSTRINGIFY)
        if self == Strategy.TRIGGER:
            return (Handler.FILE, Handler.REGEX, Handler.SHORTEN, Handler.UNSTRINGIFY)
        raise NotImplementedError()


def parse_element(value: str) -> typing.Tuple[str, typing.Optional[str], typing.List[str], typing.Optional[str]]:
    splitted = value.split(":", 1)
    definition = splitted[1] if len(splitted) == 2 else None
    splitted = splitted[0].split(",")
    options = splitted[1:]
    splitted = splitted[0].split(".", 1)
    group = splitted[1] if len(splitted) == 2 else None
    name = splitted[0]
    return name, group, options, definition


def add_matcher(subparser: argparse.ArgumentParser):
    subparser.add_argument(
        "-m",
        "--matcher",
        action="append",
        metavar="NAME[.GROUP][:DEFINITION]",
        default=[],
    )


def add_handler(subparser: argparse.ArgumentParser):
    subparser.add_argument(
        "-h",
        "--handler",
        action="append",
        metavar="NAME[.GROUP][,OPTION[,OPTION]][:DEFINITION]",
        default=[],
    )


def convert_parser(root_parser):
    convert = root_parser.add_parser("convert", help="Convert parts of JSON", add_help=False)
    add_matcher(convert)
    add_handler(convert)


def extract_parser(root_parser):
    extract = root_parser.add_parser("extract", help="Passes only matched parts of JSON", add_help=False)
    add_matcher(extract)
    add_handler(extract)
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
    filter_parser = root_parser.add_parser("filter", help="Removes matched parts of JSON", add_help=False)
    add_matcher(filter_parser)
    add_handler(filter_parser)


def trigger_parser(root_parser):
    trigger_parser = root_parser.add_parser("trigger", help="Triggers command on matched input", add_help=False)
    add_matcher(trigger_parser)
    add_handler(trigger_parser)


def build_matchers_and_handlers(parsed: argparse.Namespace) -> typing.Dict[typing.Optional[str], dict]:
    res: typing.Dict[typing.Optional[str], dict] = {}
    for matcher in parsed.matcher:
        name, group, _, definition = parse_element(matcher)
        matcher = Matcher.from_name(name).instance(definition)
        record = res.get(group, {"matcher": None, "handler": None})
        record["matcher"] = record["matcher"] | matcher if record["matcher"] else matcher
        res[group] = record

    for handler in parsed.handler:
        name, group, options, definition = parse_element(handler)
        handler = Handler.from_name(name).instance(definition, *options)
        record = res.get(group, {"matcher": None, "handler": None})
        record["handler"] = record["handler"] + handler if record["handler"] else handler
        res[group] = record

    return res


def filter_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups = build_matchers_and_handlers(parsed)
    fltr = streamson.filter.Filter()

    for record in groups.values():
        fltr.add_matcher(record["matcher"].inner, record["handler"])

    for item in input_gen:
        for output in fltr.process(item):
            if output.data:
                sys.stdout.write(bytes(output.data).decode())
    else:
        # Just return stdin
        for input_data in input_gen:
            sys.stdout.buffer.write(input_data)


def extract_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups = build_matchers_and_handlers(parsed)
    extract = streamson.extract.Extract()

    for record in groups.values():
        extract.add_matcher(record["matcher"].inner, record["handler"])

    sys.stdout.write(parsed.before)
    first = True
    for item in input_gen:
        for output in extract.process(item):
            if not first and output.kind == "Start":
                sys.stdout.write(parsed.separator)
            else:
                first = False
            if output.data:
                sys.stdout.write(bytes(output.data).decode())
    sys.stdout.write(parsed.after)


def convert_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups = build_matchers_and_handlers(parsed)
    convert = streamson.convert.Convert()

    for record in groups.values():
        convert.add_matcher(record["matcher"].inner, record["handler"])

    for item in input_gen:
        for output in convert.process(item):
            if output.data:
                sys.stdout.write(bytes(output.data).decode())


def trigger_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups = build_matchers_and_handlers(parsed)
    trigger = streamson.trigger.Trigger()

    for record in groups.values():
        trigger.add_matcher(record["matcher"].inner, record["handler"])

    for item in input_gen:
        trigger.process(item)
        sys.stdout.write(item.decode())


def main():
    version = pkg_resources.get_distribution("streamson-python").version

    parser = argparse.ArgumentParser(prog="streamson", add_help=False)
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
