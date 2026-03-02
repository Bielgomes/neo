from typing import Any, List
from core.token import Position, Token, TokenKind, reserved_keywords_map
from exceptions.neo_error import NeoError


class Lexer:
    def __init__(self, source: str) -> None:
        self.tokens = []

        self.column = 0
        self.line = 1

        self.source = source
        self.max_length = len(self.source)

    def tokenize(self) -> List[Token]:
        while not self.is_at_end():
            lexeme = self.advance()

            match lexeme:
                case "" | " " | "\r" | "\t":
                    continue
                case "\n":
                    self.line += 1
                    continue
                case "+":
                    self.add_token(kind=TokenKind.PLUS)
                case "-":
                    self.add_token(kind=TokenKind.MINUS)
                case "*":
                    self.add_token(kind=TokenKind.STAR)
                case "/":
                    self.add_token(kind=TokenKind.SLASH)
                case "#":
                    print("entrou")
                    if self.match("/"):
                        while self.peak() != "/":
                            self.advance()

                        self.consume("/")
                        self.consume("#")
                        continue

                    while self.peak() != "\n" and not self.is_at_end():
                        self.advance()
                case ">":
                    if self.match("="):
                        self.add_token(kind=TokenKind.GREATER_THAN_EQUAL)
                    else:
                        self.add_token(kind=TokenKind.GREATER_THAN)
                case "<":
                    if self.match("="):
                        self.add_token(kind=TokenKind.LESS_THAN_EQUAL)
                    else:
                        self.add_token(kind=TokenKind.LESS_THAN)
                case '"':
                    self.handle_string()
                case "=":
                    if self.match("="):
                        self.add_token(kind=TokenKind.EQUAL_EQUAL)
                    else:
                        self.add_token(kind=TokenKind.EQUAL)
                case "!":
                    if self.match("="):
                        self.add_token(kind=TokenKind.NOT_EQUAL)
                    else:
                        self.add_token(kind=TokenKind.NOT)
                case "?":
                    self.add_token(kind=TokenKind.QUESTION)
                case ":":
                    self.add_token(kind=TokenKind.COLLON)
                case ";":
                    self.add_token(kind=TokenKind.SEMICOLON)
                case "(":
                    self.add_token(kind=TokenKind.LPAREN)
                case ")":
                    self.add_token(kind=TokenKind.RPAREN)
                case "{":
                    self.add_token(kind=TokenKind.LBRACE)
                case "}":
                    self.add_token(kind=TokenKind.RBRACE)
                case _:
                    if self.is_digit(lexeme):
                        self.handle_number()
                    elif self.is_alpha(lexeme):
                        self.handle_identifier()
                    else:
                        raise NeoError(
                            line=self.line,
                            message=f"Unexpected Character '{lexeme}'",
                        )

        self.add_token(kind=TokenKind.EOF)
        return self.tokens

    def is_at_end(self) -> bool:
        return self.column >= self.max_length

    def advance(self) -> str:
        lexeme = self.source[self.column]
        self.column += 1

        return lexeme

    def peak(self) -> str:
        if self.is_at_end():
            return "\0"

        return self.source[self.column]

    def peak_next(self) -> str:
        if self.column + 1 >= self.max_length:
            return "\0"

        return self.source[self.column + 1]

    def handle_number(self) -> None:
        start_index = self.column - 1
        length = 1

        while self.is_digit(self.peak()):
            self.advance()
            length += 1

        if self.peak() == "." and self.is_digit(self.peak_next()):
            self.advance()
            length += 1

            while self.is_digit(self.peak()):
                self.advance()
                length += 1

        value = float(self.source[start_index : start_index + length])
        self.add_token(kind=TokenKind.NUMBER, literal=value)

    def handle_identifier(self) -> None:
        start_index = self.column - 1
        length = 1

        while self.is_alpha_numeric(self.peak()):
            self.advance()
            length += 1

        name = self.source[start_index : start_index + length]
        if kind := reserved_keywords_map.get(name):
            self.add_token(kind=kind, literal=None)
            return

        self.add_token(kind=TokenKind.IDENTIFIER, literal=name)

    def handle_string(self) -> None:
        start_index = self.column
        length = 0

        while self.peak() != '"' and not self.is_at_end():
            if self.peak() == "\n":
                self.line += 1
            self.advance()
            length += 1

        if self.peak() != '"':
            raise NeoError(line=self.line, message="Unterminated String")

        self.advance()

        value = self.source[start_index : start_index + length]
        self.add_token(kind=TokenKind.STRING, literal=value)

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False

        if self.peak() != expected:
            return False

        self.column += 1
        return True

    def consume(self, expected: str) -> bool:
        if not self.match(expected=expected):
            raise NeoError(
                line=self.line, message=f"Unexpected Character '{self.peak()}'"
            )

        return True

    def add_token(self, kind: TokenKind, literal: Any = None) -> None:
        position = Position(line=self.line, column=self.column)
        self.tokens.append(Token(kind=kind, position=position, literal=literal))

    def is_digit(self, d: str) -> bool:
        return d.isdigit()

    def is_alpha(self, a: str) -> bool:
        return a.isalpha()

    def is_alpha_numeric(self, n: str) -> bool:
        return self.is_digit(n) or self.is_alpha(n)
