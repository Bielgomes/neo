from abc import ABC, abstractmethod
from typing import Any
from core.token import Token


class ExprVisitor(ABC):
    @abstractmethod
    def visite_literal_expr(self, expr: "Expr.LiteralExpr") -> Any: ...

    @abstractmethod
    def visite_variable_expr(self, expr: "Expr.VariableExpr") -> Any: ...

    @abstractmethod
    def visite_assign_expr(self, expr: "Expr.AssignExpr") -> Any: ...

    @abstractmethod
    def visite_grouping_expr(self, expr: "Expr.GroupingExpr") -> Any: ...

    @abstractmethod
    def visite_unary_expr(self, expr: "Expr.UnaryExpr") -> Any: ...

    @abstractmethod
    def visite_binary_expr(self, expr: "Expr.BinaryExpr") -> Any: ...

    @abstractmethod
    def visite_ternary_expr(self, expr: "Expr.TernaryExpr") -> Any: ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor) -> any: ...

    class LiteralExpr:
        def __init__(self, value: any):
            self.value = value

        def accept(self, visitor: ExprVisitor) -> any:
            return visitor.visite_literal_expr(self)

    class Variable:
        def __init__(self, name: Token):
            self.name = name

        def accept(self, visitor: ExprVisitor) -> any:
            return visitor.visite_variable_expr(self)

    class AssignExpr:
        def __init__(self, identifier: Token, value: "Expr"):
            self.identifier = identifier
            self.value = value

        def accept(self, visitor: ExprVisitor) -> any:
            return visitor.visite_assign_expr(self)

    class GroupingExpr:
        def __init__(self, value: "Expr"):
            self.value = value

        def accept(self, visitor: ExprVisitor) -> any:
            return visitor.visite_grouping_expr(self)

    class UnaryExpr:
        def __init__(self, operator: Token, right: "Expr"):
            self.operator = operator
            self.right = right

        def accept(self, visitor: ExprVisitor) -> any:
            return visitor.visite_unary_expr(self)

    class BinaryExpr:
        def __init__(
            self,
            operator: Token,
            left: "Expr",
            right: "Expr",
        ):
            self.operator = operator
            self.left = left
            self.right = right

        def accept(self, visitor: ExprVisitor) -> any:
            return visitor.visite_binary_expr(self)

    class TernaryExpr:
        def __init__(
            self,
            condition: "Expr",
            left: "Expr",
            right: "Expr",
        ):
            self.condition = condition
            self.left = left
            self.right = right

        def accept(self, visitor: ExprVisitor) -> any:
            return visitor.visite_ternary_expr(self)
