from abc import ABC, abstractmethod
from typing import Any, List

from core.expression import Expr
from core.token import Token


class StmtVisitor(ABC):
    @abstractmethod
    def visite_expr_stmt(self, stmt: "Stmt.ExprStmt") -> Any: ...

    @abstractmethod
    def visite_let_decl_stmt(self, stmt: "Stmt.LetDeclStmt") -> None: ...

    @abstractmethod
    def visite_print_stmt(self, stmt: "Stmt.PrintStmt") -> None: ...

    @abstractmethod
    def visite_block_stmt(self, stmt: "Stmt.BlockStmt") -> None: ...

    @abstractmethod
    def visite_if_stmt(self, stmt: "Stmt.IfStmt") -> None: ...


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor) -> Any: ...

    class ExprStmt:
        def __init__(self, expr: Expr) -> None:
            self.expr = expr

        def accept(self, visitor: StmtVisitor) -> Any:
            return visitor.visite_expr_stmt(self)

    class LetDeclStmt:
        def __init__(self, identifier: Token, expr: Expr) -> None:
            self.identifier = identifier
            self.expr = expr

        def accept(self, visitor: StmtVisitor) -> None:
            visitor.visite_let_decl_stmt(self)

    class PrintStmt:
        def __init__(self, expr: Expr) -> None:
            self.expr = expr

        def accept(self, visitor: StmtVisitor) -> None:
            visitor.visite_print_stmt(self)

    class BlockStmt:
        def __init__(self, stmts: List["Stmt"]) -> None:
            self.stmts = stmts

        def accept(self, visitor: StmtVisitor) -> None:
            return visitor.visite_block_stmt(self)

    class IfStmt:
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
