import time
from typing import TYPE_CHECKING, Any, List

from core.neo_function import NeoFunction

if TYPE_CHECKING:
    from core.interpreter import Interpreter


class timeCounter(NeoFunction):
    def __init__(self):
        self.arity = 0

    def call(self, interpreter: Interpreter, arguments: List[Any]) -> int:
        return time.perf_counter()
