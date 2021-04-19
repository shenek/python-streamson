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
            spaces: typing.Optional[int]
            if definition:
                try:
                    spaces = int(definition)
                except ValueError:
                    raise ValueError("Indenter can't parse number of spaces")
            else:
                spaces = None
            return streamson.handler.IndenterHandler(spaces)
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
    ALL = auto()
    CONVERT = auto()
    FILTER = auto()
    EXTRACT = auto()
    TRIGGER = auto()

    def check_handler(self, handler: Handler):
        if handler not in self.available_handlers:
            handler.name.lower()
            print(
                f"handler `{handler.name.lower()}` can not be used in `{self.name.lower()}` strategy.", file=sys.stderr
            )
            sys.exit(1)

    @property
    def available_handlers(self) -> typing.Tuple[Handler, ...]:
        if self == Strategy.ALL:
            return (Handler.INDENTER, Handler.ANALYSER)
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


def all_parser(root_parser):
    all_parser = root_parser.add_parser("all", help="Matches parts of JSON", add_help=False)
    add_handler(all_parser)


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


def build_matchers_and_handlers(
    parsed: argparse.Namespace, strategy: Strategy
) -> typing.Tuple[
    typing.Dict[typing.Optional[str], dict],
    typing.List[streamson.matcher.Matcher],
    typing.List[streamson.handler.BaseHandler],
]:
    groups: typing.Dict[typing.Optional[str], dict] = {}
    matchers: typing.List[streamson.matcher.Matcher] = []
    handlers: typing.List[streamson.handler.BaseHandler] = []
    if hasattr(parsed, "matcher"):
        for matcher in parsed.matcher:
            name, group, _, definition = parse_element(matcher)
            matcher = Matcher.from_name(name).instance(definition)
            matchers.append(matcher)
            record = groups.get(group, {"matcher": None, "handler": None})
            record["matcher"] = record["matcher"] | matcher if record["matcher"] else matcher
            groups[group] = record

    for handler in parsed.handler:
        name, group, options, definition = parse_element(handler)
        hndlr = Handler.from_name(name)
        strategy.check_handler(hndlr)
        handler = hndlr.instance(definition, *options)
        handlers.append(handler)
        record = groups.get(group, {"matcher": None, "handler": None})
        record["handler"] = record["handler"] + handler if record["handler"] else handler
        groups[group] = record

    return groups, matchers, handlers


def all_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups, _, handlers = build_matchers_and_handlers(parsed, Strategy.ALL)
    is_converter = any(e["handler"].is_converter() for e in groups.values())

    all_strategy = streamson.all.All(is_converter)

    for record in groups.values():
        all_strategy.add_handler(record["handler"])

    for item in input_gen:
        for output in all_strategy.process(item):
            if is_converter and output and output[1]:
                sys.stdout.write(output[1].decode())

        if not is_converter:
            sys.stdout.write(item.decode())

    if is_converter:
        for output in all_strategy.terminate():
            if output and output[1]:
                sys.stdout.write(output[1].decode())
    else:
        all_strategy.terminate()

    for handler in handlers:
        # analyser handler specific
        if isinstance(handler, streamson.handler.AnalyserHandler):
            print("JSON structure:", file=sys.stderr)
            for item in handler.results():
                print(f"  {item[0] or '<root>'}: {item[1]}", file=sys.stderr)


def filter_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups, _, _ = build_matchers_and_handlers(parsed, Strategy.FILTER)
    fltr = streamson.filter.Filter()

    for record in groups.values():
        fltr.add_matcher(record["matcher"].inner, record["handler"])

    for item in input_gen:
        for output in fltr.process(item):
            if output and output[1]:
                sys.stdout.write(output[1].decode())

    for output in fltr.terminate():
        if output and output[1]:
            sys.stdout.write(output[1].decode())


def extract_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups, _, _ = build_matchers_and_handlers(parsed, Strategy.EXTRACT)
    extract = streamson.extract.Extract()

    for record in groups.values():
        extract.add_matcher(record["matcher"].inner, record["handler"])

    sys.stdout.write(parsed.before)
    first = True
    for item in input_gen:
        for output in extract.process(item):
            if output:
                path, data = output
                if data:
                    sys.stdout.write(data.decode())
                else:
                    if not first:
                        sys.stdout.write(parsed.separator)
                    else:
                        first = False

    for output in extract.terminate():
        if output:
            path, data = output
            if data:
                sys.stdout.write(data.decode())
            if path:
                if not first:
                    sys.stdout.write(parsed.separator)
                else:
                    first = False

    sys.stdout.write(parsed.after)


def convert_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups, _, _ = build_matchers_and_handlers(parsed, Strategy.CONVERT)
    convert = streamson.convert.Convert()

    for record in groups.values():
        convert.add_matcher(record["matcher"].inner, record["handler"])

    for item in input_gen:
        for output in convert.process(item):
            if output and output[1]:
                sys.stdout.write(output[1].decode())

    for output in convert.terminate():
        if output and output[1]:
            sys.stdout.write(output[1].decode())


def trigger_strategy(parsed: argparse.Namespace, input_gen: typing.Generator[bytes, None, None]):
    groups, _, _ = build_matchers_and_handlers(parsed, Strategy.TRIGGER)
    trigger = streamson.trigger.Trigger()

    for record in groups.values():
        trigger.add_matcher(record["matcher"].inner, record["handler"])

    for item in input_gen:
        trigger.process(item)
        sys.stdout.write(item.decode())

    trigger.terminate()


def main():
    version = pkg_resources.get_distribution("streamson-python").version

    parser = argparse.ArgumentParser(prog="streamson", add_help=False)
    parser.add_argument("--version", action="version", version=version)
    parser.add_argument("-b", "--buffer-size", type=int, default=2 ** 20)

    strategies = parser.add_subparsers(help="strategies", dest="strategy")
    strategies.required = True
    all_parser(strategies)
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
    elif options.strategy == "all":
        all_strategy(options, input_generator())


if __name__ == "__main__":
    main()
