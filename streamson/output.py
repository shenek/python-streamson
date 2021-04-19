import typing

PythonOutput = typing.Optional[typing.Tuple[typing.Optional[str], typing.Optional[bytes]]]


class Output:
    """ Buffers Output complete output JSONs """

    def __init__(self, output_generator: typing.Generator[PythonOutput, None, None]):
        self.output_generator = output_generator
        self.path: typing.Optional[str] = None
        self.data = bytes()

    def generator(self) -> typing.Generator[typing.Tuple[typing.Optional[str], bytes], None, None]:

        for e in self.output_generator:
            if e is None:
                # End was reached
                yield self.path, self.data
                self.data = bytes()
                self.path = None
            else:
                path, data = e
                if data:
                    # Feed was reached
                    self.data += data
                else:
                    # Start was reached
                    self.path = path
