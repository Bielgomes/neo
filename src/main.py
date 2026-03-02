from pathlib import Path

from core.interpreter import Interpreter
from core.lexer import Lexer
from core.parser import Parser

import sys

from exceptions.neo_error_base import NeoErrorBase


def main() -> None:
    if len(sys.argv) > 2:
        print("Run: python src/main.py [script]")
    elif len(sys.argv) == 2:
        if sys.argv[1].split(".")[-1] != "fds":
            print("Error: File must have a .fds extension.")
        elif not Path.exists(sys.argv[1]):
            print(f"Error: File {sys.argv[1]} does not exists.")
        else:
            run_file(sys.argv[1])
    else:
        prompt()


def run(source: str) -> None:
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        statements = parser.parse()

        Interpreter().interpret(statements)
    except NeoErrorBase as err:
        print(err)
        return


def run_file(path: str) -> None:
    with open(path) as script:
        source = script.read()
        run(source)


def prompt() -> None:
    while True:
        source = input("> ")
        run(source)


if __name__ == "__main__":
    main()
