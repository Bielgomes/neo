from enum import Enum, auto
from typing import Any


class TokenKind(Enum):
    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    NULL = auto()

    # Mathematic
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    # Relational
    EQUAL_EQUAL = auto()
    NOT_EQUAL = auto()
    GREATER_THAN = auto()
    LESS_THAN = auto()
    GREATER_THAN_EQUAL = auto()
    LESS_THAN_EQUAL = auto()

    # Logic
    AND = auto()
    OR = auto()
    NOT = auto()

    # Boolean
    TRUE = auto()
    FALSE = auto()

    # Special
    EQUAL = auto()
    COLLON = auto()
    QUESTION = auto()
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LET = auto()
    IF = auto()
    ELSE = auto()
    PRINT = auto()
    EOF = auto()


reserved_keywords_map = {
    "let": TokenKind.LET,
    "if": TokenKind.IF,
    "else": TokenKind.ELSE,
    "print": TokenKind.PRINT,
    "true": TokenKind.TRUE,
    "false": TokenKind.FALSE,
    "null": TokenKind.NULL,
    "and": TokenKind.AND,
    "or": TokenKind.OR,
}


class Position:
    def __init__(self, line: int, column: int) -> None:
        self.line = line
        self.column = column

    def __str__(self) -> str:
        return f"at Line: {self.line} Column: {self.column}"


class Token:
    def __init__(
        self, kind: TokenKind, position: Position, literal: Any = None
    ) -> None:
        self.kind: TokenKind = kind
        self.literal = literal
        self.position = position

    @property
    def lexeme(self) -> str:
        match self.kind:
            case TokenKind.IDENTIFIER:
                return self.literal or ""
            case TokenKind.NUMBER:
                if self.literal.is_integer():
                    return str(int(self.literal))

                return str(self.literal)
            case TokenKind.STRING:
                return self.literal
            case TokenKind.NULL:
                return "null"

            # Mathematic
            case TokenKind.PLUS:
                return "+"
            case TokenKind.MINUS:
                return "-"
            case TokenKind.STAR:
                return "*"
            case TokenKind.SLASH:
                return "/"

            # Relational
            case TokenKind.EQUAL_EQUAL:
                return "=="
            case TokenKind.NOT_EQUAL:
                return "!="
            case TokenKind.GREATER_THAN:
                return ">"
            case TokenKind.LESS_THAN:
                return "<"
            case TokenKind.GREATER_THAN_EQUAL:
                return ">="
            case TokenKind.LESS_THAN_EQUAL:
                return "<="

            # Logic
            case TokenKind.AND:
                return "and"
            case TokenKind.OR:
                return "or"
            case TokenKind.NOT:
                return "!"

            # Boolean
            case TokenKind.TRUE:
                return "true"
            case TokenKind.FALSE:
                return "false"

            # EOF
            case TokenKind.EQUAL:
                return "="
            case TokenKind.COLLON:
                return ":"
            case TokenKind.QUESTION:
                return "?"
            case TokenKind.SEMICOLON:
                return ";"
            case TokenKind.LPAREN:
                return "("
            case TokenKind.RPAREN:
                return ")"
            case TokenKind.LBRACE:
                return "{"
            case TokenKind.RBRACE:
                return "}"
            case TokenKind.LET:
                return "let"
            case TokenKind.IF:
                return "if"
            case TokenKind.ELSE:
                return "else"
            case TokenKind.PRINT:
                return "print"
            case TokenKind.EOF:
                return "EOF"
