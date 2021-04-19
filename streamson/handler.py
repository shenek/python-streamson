import typing

from streamson.streamson import (
    AnalyserHandler,
    BaseHandler,
    BufferHandler,
    FileHandler,
    IndenterHandler,
    IndexerHandler,
    PythonHandler,
    PythonToken,
    RegexHandler,
    ReplaceHandler,
    ShortenHandler,
    StdoutHandler,
    UnstringifyHandler,
)

__all__ = [
    "AnalyserHandler",
    "BaseHandler",
    "BufferHandler",
    "FileHandler",
    "IndenterHandler",
    "IndexerHandler",
    "PythonHandler",
    "RegexHandler",
    "ReplaceHandler",
    "ShortenHandler",
    "StdoutHandler",
    "UnstringifyHandler",
]


class PythonConverterHandler(PythonHandler):
    """Buffers data of each match and performs converstion when the match terminates"""

    def __new__(cls, converter_function: typing.Callable[[bytes], bytes], require_path: bool = True):
        buff = [bytes()]  # we need to encapsulate bytes here

        def start(path: typing.Optional[str], matcher_idx: int, token: PythonToken) -> typing.Optional[bytes]:
            return None

        def feed(data: bytes, matcher_idx: int) -> typing.Optional[bytes]:
            buff[0] += bytes(data)
            return None

        def end(path: typing.Optional[str], matcher_idx: int, token: PythonToken) -> typing.Optional[bytes]:
            res = converter_function(buff[0])
            # clear the buffer
            buff[0] = bytes()
            return res

        res = super().__new__(cls, start, feed, end, require_path=require_path, is_converter=True)
        res.buffer = buff
        res.converter_function = converter_function

        return res
