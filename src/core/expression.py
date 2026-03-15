from abc import ABC, abstractmethod
from typing import Any, List
from core.token import Token


class ExprVisitor(ABC):
    @abstractmethod
    def visite_literal_expr(self, expr: "Expr.Literal") -> Any: ...

    @abstractmethod
    def visite_variable_expr(self, expr: "Expr.Variable") -> Any: ...

    @abstractmethod
    def visite_assign_expr(self, expr: "Expr.Assign") -> Any: ...

    @abstractmethod
    def visite_call_expr(self, expr: "Expr.Call") -> Any: ...

    @abstractmethod
    def visite_grouping_expr(self, expr: "Expr.Grouping") -> Any: ...

    @abstractmethod
    def visite_unary_expr(self, expr: "Expr.Unary") -> Any: ...

    @abstractmethod
    def visite_binary_expr(self, expr: "Expr.Binary") -> Any: ...

    @abstractmethod
    def visite_ternary_expr(self, expr: "Expr.Ternary") -> Any: ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> Any: ...

    class Literal:
        def __init__(self, value: Any):
            self.value = value

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_literal_expr(self)

    class Variable:
        def __init__(self, name: Token):
            self.name = name

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_variable_expr(self)

    class Assign:
        def __init__(self, identifier: Token, value: "Expr"):
            self.identifier = identifier
            self.value = value

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_assign_expr(self)

    class Call:
        def __init__(self, calle: "Expr", paren: Token, arguments: List["Expr"]):
            self.calle = calle
            self.paren = paren
            self.arguments = arguments

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_call_expr(self)

    class Grouping:
        def __init__(self, value: "Expr"):
            self.value = value

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_grouping_expr(self)

    class Unary:
        def __init__(self, operator: Token, right: "Expr"):
            self.operator = operator
            self.right = right

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_unary_expr(self)

    class Binary:
        def __init__(
            self,
            operator: Token,
            left: "Expr",
            right: "Expr",
        ):
            self.operator = operator
            self.left = left
            self.right = right

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_binary_expr(self)

    class Ternary:
        def __init__(
            self,
            condition: "Expr",
            left: "Expr",
            right: "Expr",
        ):
            self.condition = condition
            self.left = left
            self.right = right

        def accept(self, visitor: ExprVisitor) -> Any:
            return visitor.visite_ternary_expr(self)
