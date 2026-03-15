from typing import TYPE_CHECKING, Any, List


from core.environment import Environment
from core.neo_callable import NeoCallable
from core.statement import Stmt

if TYPE_CHECKING:
    from core.interpreter import Interpreter


class NeoFunction(NeoCallable):
    def __init__(self, declaration: Stmt.Function):
        self.arity = len(declaration.parameters)
        self.declaration = declaration

    def call(self, interpreter: Interpreter, arguments: List[Any]) -> Any:
        new_environment = Environment()
        for parameter, argument in zip(self.declaration.parameters, arguments):
            new_environment.declare(name=parameter, value=argument)

        return interpreter.execute_block(
            environment=new_environment, stmt=self.declaration.body
        )

    def __str__(self):
        return f"<fn {self.declaration.name.lexeme}>"
