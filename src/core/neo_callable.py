from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, List


if TYPE_CHECKING:
    from core.interpreter import Interpreter


class NeoCallable(ABC):
    @property
    def arity(self) -> int:
        return self._arity

    @arity.setter
    def arity(self, arity: int) -> None:
        self._arity = arity

    @abstractmethod
    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any: ...
