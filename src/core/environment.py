from typing import Any

from core.token import Token
from exceptions.neo_runtime_error import NeoRuntimeError


class Environment:
    def __init__(self, parent_environment: "Environment" | None = None) -> None:
        self.parent_environment = parent_environment
        self.environment = {}

    def declare(self, name: Token, value: Any) -> None:
        if name.lexeme in self.environment:
            raise NeoRuntimeError(
                token=name, message=f"'{name.lexeme}' already declared in this context"
            )

        self.environment[name.lexeme] = value

    def get_value(self, name: Token) -> Any:
        if name.lexeme in self.environment:
            return self.environment[name.lexeme]

        if self.parent_environment is not None:
            return self.parent_environment.get_value(name)

        raise NeoRuntimeError(
            token=name, message=f"'{name.lexeme}' not declared in this context"
        )

    def set_value(self, name: Token, value: Any) -> Any:
        if name.lexeme in self.environment:
            self.environment[name.lexeme] = value
            return value

        if self.parent_environment is not None:
            return self.parent_environment.set_value(name, value)

        raise NeoRuntimeError(
            token=name, message=f"'{name.lexeme}' not declared in this context"
        )
