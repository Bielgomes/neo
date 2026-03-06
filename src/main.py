from pathlib import Path

from core.interpreter import Interpreter
from core.lexer import Lexer
from core.parser import Parser

import sys

from exceptions.neo_error_base import NeoErrorBase


class NeoProgram:
    def __init__(self):
        self.interpreter = Interpreter()

    def run(self, source: str) -> None:
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            parser = Parser(tokens)
            statements = parser.parse()

            self.interpreter.interpret(statements)
        except NeoErrorBase as err:
            print(err)
            return

    def run_file(self, path: str) -> None:
        with open(path) as script:
            source = script.read()
            self.run(source)

    def prompt(self) -> None:
        while True:
            source = input("> ")
            self.run(source)


def main() -> None:
    neoProgram = NeoProgram()

    if len(sys.argv) > 2:
        print("Run: python src/main.py [script]")
        return

    if len(sys.argv) == 2:
        if sys.argv[1].split(".")[-1] != "neo":
            print("[Error]: File must have a .neo extension.")
            return

        if not Path.exists(sys.argv[1]):
            print(f"[Error]: File {sys.argv[1]} does not exists.")
            return

        neoProgram.run_file(sys.argv[1])
        return

    neoProgram.prompt()


if __name__ == "__main__":
    main()
