from typing import Any

from core.environment import Environment
from core.expression import Expr, ExprVisitor
from core.statement import Stmt, StmtVisitor
from core.token import Token, TokenKind
from exceptions.neo_runtime_error import NeoRuntimeError


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.environment = Environment()

    def interpret(self, statements: Stmt):
        for statement in statements:
            self.execute(statement)

    def visite_expr_stmt(self, stmt: "Stmt.ExprStmt") -> Any:
        return self.evaluate(stmt.expr)

    def visite_let_decl_stmt(self, stmt: "Stmt.LetDeclStmt") -> None:
        value = None
        if stmt.expr is not None:
            value = self.evaluate(stmt.expr)

        self.environment.declare(name=stmt.identifier, value=value)

    def visite_print_stmt(self, stmt: "Stmt.PrintStmt") -> None:
        value = self.evaluate(stmt.expr)
        print(self.stringfy(value))

    def visite_block_stmt(self, stmt: "Stmt.BlockStmt") -> None:
        previous = self.environment

        for stmt in stmt.stmts:
            self.environment = Environment(parent_environment=previous)
            self.execute(stmt)

        self.environment = previous

    def visite_if_stmt(self, stmt: "Stmt.IfStmt") -> None:
        condition = self.evaluate(stmt.condition)
        if self.is_truthy(condition):
            return self.execute(stmt.then_branch)
        elif stmt.else_branch is not None and self.is_truthy(stmt.else_branch):
            return self.execute(stmt.else_branch)

        return

    def visite_literal_expr(self, expr: "Expr.LiteralExpr") -> Any:
        return expr.value

    def visite_variable_expr(self, expr: "Expr.VariableExpr") -> Any:
        return self.environment.get_value(expr.name)

    def visite_assign_expr(self, expr: "Expr.AssignExpr") -> Any:
        value = self.evaluate(expr.value)
        self.environment.set_value(name=expr.identifier, value=value)
        return value

    def visite_grouping_expr(self, expr: "Expr.GroupingExpr") -> Any:
        return self.evaluate(expr.value)

    def visite_unary_expr(self, expr: "Expr.UnaryExpr") -> Any:
        right = self.evaluate(expr.right)

        match expr.operator.kind:
            case TokenKind.NOT:
                return not self.is_truthy(right)
            case TokenKind.MINUS:
                self.check_number_operand(operator=expr.operator, operand=right)
                return -right

    def visite_binary_expr(self, expr: "Expr.BinaryExpr") -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)

        match expr.operator.kind:
            # Mathematic
            case TokenKind.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            case TokenKind.SLASH:
                if right == 0:
                    raise NeoRuntimeError(token=right, message="Division by zero")

                self.check_number_operands(expr.operator, left, right)
                return left / right
            case TokenKind.PLUS:
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, str) or isinstance(right, str):
                    return self.stringfy(left) + self.stringfy(right)
                return left + right
            case TokenKind.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right

            # Relational
            case TokenKind.EQUAL_EQUAL:
                return left == right
            case TokenKind.NOT_EQUAL:
                return left != right
            case TokenKind.GREATER_THAN:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case TokenKind.GREATER_THAN_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenKind.LESS_THAN:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case TokenKind.LESS_THAN_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right

            # Logic
            case TokenKind.AND:
                return self.is_truthy(left) and self.is_truthy(right)
            case TokenKind.OR:
                return self.is_truthy(left) or self.is_truthy(right)
            case TokenKind.NULLISH:
                if left is not None:
                    return left

                return right

    def visite_ternary_expr(self, expr: "Expr.TernaryExpr") -> Any:
        condition = self.evaluate(expr.condition)
        if self.is_truthy(condition):
            return self.evaluate(expr.left)

        return self.evaluate(expr.right)

    def evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def check_number_operand(self, operator: Token, operand: Any) -> bool:
        if isinstance(operand, (float, int)):
            return True

        raise NeoRuntimeError(
            token=operator, message=f"{operator.lexeme} operands must be numbers"
        )

    def check_number_operands(self, operator: Token, left: Any, right: Any) -> bool:
        return self.check_number_operand(
            operator=operator, operand=left
        ) and self.check_number_operand(operator=operator, operand=right)

    def stringfy(self, value: Any) -> str:
        if value is None:
            return "null"

        if isinstance(value, float):
            text = str(value)
            if text.endswith(".0"):
                text = text.replace(".0", "")
            return text

        if isinstance(value, bool):
            text = str(value).lower()
            return text

        return str(value)

    def is_truthy(self, value: Any) -> bool:
        if value == "null":
            return False

        return bool(value)
