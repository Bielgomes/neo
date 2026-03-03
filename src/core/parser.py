from typing import List
from core.statement import Stmt
from core.token import Token, TokenKind
from core.expression import Expr
from exceptions.neo_error import NeoError


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.position = 0

        self.max_position = len(self.tokens)

    def parse(self) -> List[Stmt]:
        statments: List[Stmt] = []

        while not self.is_at_end():
            statments.append(self.statement())

        return statments

    def statement(self) -> Stmt:
        if self.match([TokenKind.LET]):
            return self.let_declaration_statement()
        if self.match([TokenKind.LBRACE]):
            return self.block_statement()
        if self.match([TokenKind.PRINT]):
            return self.print_statement()
        if self.match([TokenKind.IF]):
            return self.if_statement()

        return self.expression_statement()

    def if_statement(self) -> Stmt:
        self.consume(kind=TokenKind.LPAREN, message="Expected '('")
        condition = self.parse_expression()
        self.consume(kind=TokenKind.RPAREN, message="Expected ')'")
        than_branch = self.statement()

        else_branch = None
        if self.match([TokenKind.ELSE]):
            else_branch = self.statement()

        return Stmt.IfStmt(
            condition=condition, then_branch=than_branch, else_branch=else_branch
        )

    def block_statement(self) -> Stmt:
        stmts: List[Stmt] = []

        while not self.match([TokenKind.RBRACE]):
            if self.match([TokenKind.EOF]):
                raise NeoError(line=self.peek().position.line, message="Expected '}'")

            stmt = self.statement()
            stmts.append(stmt)

        return Stmt.BlockStmt(stmts)

    def print_statement(self) -> Stmt:
        self.consume(kind=TokenKind.LPAREN, message="Expected '('")
        expr = self.parse_expression()
        self.consume(kind=TokenKind.RPAREN, message="Expected ')'")
        self.consume(kind=TokenKind.SEMICOLON, message="Expected ';'")
        return Stmt.PrintStmt(expr)

    def let_declaration_statement(self) -> Stmt:
        identifier = self.consume(
            kind=TokenKind.IDENTIFIER, message="Expected variable name"
        )

        expr = None
        if self.match([TokenKind.EQUAL]):
            expr = self.parse_expression()

        self.consume(kind=TokenKind.SEMICOLON, message="Expected ';'")
        return Stmt.LetDeclStmt(identifier=identifier, expr=expr)

    def expression_statement(self) -> Stmt:
        expr = self.parse_expression()
        self.consume(kind=TokenKind.SEMICOLON, message="Expected ';'")
        return Stmt.ExprStmt(expr)

    def parse_expression(self) -> Expr:
        return self.parse_assignment()

    def parse_assignment(self) -> Expr:
        expr = self.parse_nullish()

        if self.match([TokenKind.EQUAL]):
            equals = self.previous()
            value = self.parse_assignment()
            if isinstance(expr, Expr.Variable):
                return Expr.AssignExpr(identifier=expr.name, value=value)

            raise NeoError(
                line=equals.position.line,
                message="Invalid assignment target, expected variable",
            )

        return expr

    def parse_nullish(self) -> Expr:
        expr = self.parse_ternary()

        while self.match([TokenKind.NULLISH]):
            operator = self.previous()
            right = self.parse_ternary()
            expr = Expr.BinaryExpr(operator=operator, left=expr, right=right)

        return expr

    def parse_ternary(self) -> Expr:
        expr = self.parse_logicalor()

        if self.match([TokenKind.QUESTION]):
            left = self.parse_expr()
            self.consume(kind=TokenKind.COLLON, message="Expected ':'")
            right = self.parse_ternary()

            expr = Expr.TernaryExpr(condition=expr, left=left, right=right)

        return expr

    def parse_logicalor(self) -> Expr:
        expr = self.parse_logicaland()

        while self.match([TokenKind.OR]):
            operator = self.previous()
            right = self.parse_logicaland()

            expr = Expr.BinaryExpr(operator=operator, left=expr, right=right)

        return expr

    def parse_logicaland(self) -> Expr:
        expr = self.parse_equality()

        while self.match([TokenKind.AND]):
            operator = self.previous()
            right = self.parse_equality()

            expr = Expr.BinaryExpr(operator=operator, left=expr, right=right)

        return expr

    def parse_equality(self) -> Expr:
        expr = self.parse_comparison()

        while self.match(
            [
                TokenKind.EQUAL_EQUAL,
                TokenKind.NOT_EQUAL,
            ]
        ):
            operator = self.previous()
            right = self.parse_comparison()

            expr = Expr.BinaryExpr(operator=operator, left=expr, right=right)

        return expr

    def parse_comparison(self) -> Expr:
        expr = self.parse_term()

        while self.match(
            [
                TokenKind.GREATER_THAN,
                TokenKind.GREATER_THAN_EQUAL,
                TokenKind.LESS_THAN,
                TokenKind.LESS_THAN_EQUAL,
            ]
        ):
            operator = self.previous()
            right = self.parse_factor()

            expr = Expr.BinaryExpr(operator=operator, left=expr, right=right)

        return expr

    def parse_term(self) -> Expr:
        expr = self.parse_factor()

        while self.match([TokenKind.PLUS, TokenKind.MINUS]):
            operator = self.previous()
            right = self.parse_factor()

            expr = Expr.BinaryExpr(operator=operator, left=expr, right=right)

        return expr

    def parse_factor(self) -> Expr:
        expr = self.parse_unary()

        while self.match([TokenKind.STAR, TokenKind.SLASH]):
            operator = self.previous()
            right = self.parse_unary()

            expr = Expr.BinaryExpr(operator=operator, left=expr, right=right)

        return expr

    def parse_unary(self):
        if self.match([TokenKind.NOT, TokenKind.MINUS]):
            operator = self.previous()
            right = self.parse_primary()

            return Expr.UnaryExpr(operator=operator, right=right)

        return self.parse_primary()

    def parse_primary(self):
        if self.match([TokenKind.TRUE]):
            return Expr.LiteralExpr(True)
        if self.match([TokenKind.FALSE]):
            return Expr.LiteralExpr(False)
        if self.match([TokenKind.NULL]):
            return Expr.LiteralExpr(None)
        if self.match([TokenKind.IDENTIFIER]):
            return Expr.Variable(self.previous())

        if self.match([TokenKind.NUMBER, TokenKind.STRING]):
            return Expr.LiteralExpr(self.previous().literal)

        if self.match([TokenKind.LPAREN]):
            expr = self.parse_expression()
            self.consume(kind=TokenKind.RPAREN, message="Expected )")
            return Expr.GroupingExpr(value=expr)

        raise NeoError(line=self.peek().position.line, message="Expected expression")

    def is_at_end(self) -> bool:
        return self.peek().kind == TokenKind.EOF

    def check(self, kind: TokenKind) -> bool:
        return self.peek().kind == kind

    def consume(self, kind: TokenKind, message: str) -> bool:
        if self.check(kind=kind):
            return self.advance()

        raise NeoError(line=self.peek().position.line, message=message)

    def match(self, kinds: List[TokenKind]) -> bool:
        for kind in kinds:
            if self.check(kind=kind):
                self.advance()
                return True

        return False

    def advance(self) -> Token:
        if not self.is_at_end():
            self.position += 1

        return self.previous()

    def peek(self) -> Token:
        return self.tokens[self.position]

    def previous(self) -> Token:
        return self.tokens[self.position - 1]
