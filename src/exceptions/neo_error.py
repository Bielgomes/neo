from exceptions.neo_error_base import NeoErrorBase


class NeoError(NeoErrorBase):
    def __init__(self, line: int, message: str):
        self.line = line
        super().__init__(message)

    def __str__(self):
        return f"[Error]: {self.message} at Line: {self.line}."
