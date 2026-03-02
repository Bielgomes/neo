from core.token import Token
from exceptions.neo_error_base import NeoErrorBase


class NeoRuntimeError(NeoErrorBase):
    def __init__(self, token: Token, message: str):
        self.token = token
        super().__init__(message)

    def __str__(self):
        return f"[Runtime Error]: {self.message} {self.token.position}."
