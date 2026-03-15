from abc import ABC, abstractmethod
from typing import Any, List

from core.expression import Expr
from core.token import Token


class StmtVisitor(ABC):
    @abstractmethod
    def visite_expr_stmt(self, stmt: "Stmt.Expr") -> Any: ...

    @abstractmethod
    def visite_let_decl_stmt(self, stmt: "Stmt.LetDecl") -> None: ...

    @abstractmethod
    def visite_print_stmt(self, stmt: "Stmt.Print") -> None: ...

    @abstractmethod
    def visite_block_stmt(self, stmt: "Stmt.Block") -> None: ...

    @abstractmethod
    def visite_if_stmt(self, stmt: "Stmt.If") -> None: ...

    @abstractmethod
    def visite_while_stmt(self, stmt: "Stmt.While") -> None: ...

    @abstractmethod
    def visite_fn_stmt(self, stmt: "Stmt.Function") -> None: ...


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any: ...

    class Expr:
        def __init__(self, expr: Expr) -> None:
            self.expr = expr

        def accept(self, visitor: StmtVisitor) -> Any:
            return visitor.visite_expr_stmt(self)

    class LetDecl:
        def __init__(self, identifier: Token, expr: Expr) -> None:
            self.identifier = identifier
            self.expr = expr

        def accept(self, visitor: StmtVisitor) -> None:
            visitor.visite_let_decl_stmt(self)

    class Print:
        def __init__(self, expr: Expr) -> None:
            self.expr = expr

        def accept(self, visitor: StmtVisitor) -> None:
            visitor.visite_print_stmt(self)

    class Block:
        def __init__(self, stmts: List["Stmt"]) -> None:
            self.stmts = stmts

        def accept(self, visitor: StmtVisitor) -> None:
            return visitor.visite_block_stmt(self)

    class If:
        def __init__(
            self,
            condition: Expr,
            then_branch: "Stmt",
            else_branch: "Stmt" | None = None,
        ) -> None:
            self.condition = condition
            self.then_branch = then_branch
            self.else_branch = else_branch

        def accept(self, visitor: StmtVisitor) -> None:
            return visitor.visite_if_stmt(self)

    class While:
        def __init__(
            self,
            condition: Expr,
            body: "Stmt",
        ):
            self.condition = condition
            self.body = body

        def accept(self, visitor: StmtVisitor) -> None:
            return visitor.visite_while_stmt(self)

    class Function:
        def __init__(self, name: Token, parameters: List[Token], body: "Stmt"):
            self.name = name
            self.parameters = parameters
            self.body = body

        def accept(self, visitor: StmtVisitor) -> None:
            return visitor.visite_fn_stmt(self)
