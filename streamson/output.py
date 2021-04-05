import typing
from streamson.streamson import PythonOutput


class Output:
    """ Buffers Output complete output JSONs """

    def __init__(self, output_generator: typing.Generator[PythonOutput, None, None]):
        self.output_generator = output_generator
        self.path: typing.Optional[str] = None
        self.data = bytes()

    def generator(self) -> typing.Generator[typing.Tuple[typing.Optional[str], bytes], None, None]:

        for e in self.output_generator:
            if e.kind == "Start":
                self.path = e.path
            elif e.kind == "Data":
                self.data += bytes(e.data)
            elif e.kind == "End":
                yield self.path, self.data
                self.data = bytes()
                self.path = None
