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
        statements: List[Stmt] = []

        while not self.is_at_end():
            statements.append(self.declaration())

        return statements

    def declaration(self) -> Stmt:
        if self.match([TokenKind.LET]):
            return self.let_declaration_statement()
        if self.match([TokenKind.FN]):
            return self.fn_statement()

        return self.statement()

    def statement(self) -> Stmt:
        if self.match([TokenKind.LBRACE]):
            return self.block_statement()
        if self.match([TokenKind.PRINT]):
            return self.print_statement()
        if self.match([TokenKind.IF]):
            return self.if_statement()
        if self.match([TokenKind.FOR]):
            return self.for_statement()
        if self.match([TokenKind.WHILE]):
            return self.while_statement()

        return self.expression_statement()

    def for_statement(self) -> Stmt:
        self.consume(kind=TokenKind.LPAREN, message="Expected '(' after 'for'.")

        initializer = None
        if self.match([TokenKind.SEMICOLON]):
            initializer = None
        elif self.match([TokenKind.LET]):
            initializer = self.let_declaration_statement()
        else:
            initializer = self.expression_statement()

        condition = None
        if not self.check(TokenKind.SEMICOLON):
            condition = self.parse_expression()

        self.consume(
            kind=TokenKind.SEMICOLON, message="Expected ';' after loop condition."
        )

        increment = None
        if not self.check(TokenKind.RPAREN):
            increment = self.parse_expression()

        self.consume(
            kind=TokenKind.RPAREN, message="Expected ')' after loop increment."
        )

        body = self.declaration()
        if increment is not None:
            body = Stmt.Block([body, increment])

        condition = condition if condition is not None else Expr.Literal(True)
        body = Stmt.While(condition=condition, body=body)

        if initializer is not None:
            body = Stmt.Block([initializer, body])

        return body

    def while_statement(self) -> Stmt:
        self.consume(kind=TokenKind.LPAREN, message="Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(kind=TokenKind.RPAREN, message="Expected ')'")
        body = self.declaration()

        return Stmt.While(condition=condition, body=body)

    def fn_statement(self) -> Stmt:
        name = self.consume(kind=TokenKind.IDENTIFIER, message="Expected function name")
        self.consume(kind=TokenKind.LPAREN, message="Expected '(' after 'function'")

        parameters = []

        if not self.check(kind=TokenKind.RPAREN):
            while True:
                if len(parameters) > 255:
                    raise NeoError(
                        line=self.peek().position.line,
                        message="Can't have more than 255 parameters",
                    )

                parameters.append(
                    self.consume(kind=TokenKind.IDENTIFIER, message="Expected argument")
                )

                if self.match([TokenKind.COMMA]):
                    continue

                break

        self.consume(kind=TokenKind.RPAREN, message="Expected ')'")
        self.consume(kind=TokenKind.LBRACE, message="Expected '{' before function body")
        body: Stmt.Block = self.block_statement()
        return Stmt.Function(name=name, parameters=parameters, body=body)

    def if_statement(self) -> Stmt:
        self.consume(kind=TokenKind.LPAREN, message="Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(kind=TokenKind.RPAREN, message="Expected ')'")
        than_branch = self.statement()

        else_branch = None
        if self.match([TokenKind.ELSE]):
            else_branch = self.statement()

        return Stmt.If(
            condition=condition, then_branch=than_branch, else_branch=else_branch
        )

    def block_statement(self) -> Stmt:
        stmts: List[Stmt] = []

        while not self.match([TokenKind.RBRACE]):
            if self.match([TokenKind.EOF]):
                raise NeoError(line=self.peek().position.line, message="Expected '}'")

            stmt = self.declaration()
            stmts.append(stmt)

        return Stmt.Block(stmts)

    def print_statement(self) -> Stmt:
        self.consume(kind=TokenKind.LPAREN, message="Expected '(' after 'print'")
        expr = self.parse_expression()
        self.consume(kind=TokenKind.RPAREN, message="Expected ')'")
        self.consume(kind=TokenKind.SEMICOLON, message="Expected ';'")
        return Stmt.Print(expr)

    def let_declaration_statement(self) -> Stmt:
        identifier = self.consume(
            kind=TokenKind.IDENTIFIER, message="Expected variable name"
        )

        expr = None
        if self.match([TokenKind.EQUAL]):
            expr = self.parse_expression()

        self.consume(kind=TokenKind.SEMICOLON, message="Expected ';'")
        return Stmt.LetDecl(identifier=identifier, expr=expr)

    def expression_statement(self) -> Stmt:
        expr = self.parse_expression()
        self.consume(kind=TokenKind.SEMICOLON, message="Expected ';'")
        return Stmt.Expr(expr)

    def parse_expression(self) -> Expr:
        return self.parse_assignment()

    def parse_assignment(self) -> Expr:
        expr = self.parse_nullish()

        if self.match([TokenKind.EQUAL]):
            equals = self.previous()
            value = self.parse_assignment()
            if isinstance(expr, Expr.Variable):
                return Expr.Assign(identifier=expr.name, value=value)

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
            expr = Expr.Binary(operator=operator, left=expr, right=right)

        return expr

    def parse_ternary(self) -> Expr:
        expr = self.parse_logicalor()

        if self.match([TokenKind.QUESTION]):
            left = self.parse_expression()
            self.consume(kind=TokenKind.COLLON, message="Expected ':'")
            right = self.parse_ternary()

            expr = Expr.Ternary(condition=expr, left=left, right=right)

        return expr

    def parse_logicalor(self) -> Expr:
        expr = self.parse_logicaland()

        while self.match([TokenKind.OR]):
            operator = self.previous()
            right = self.parse_logicaland()

            expr = Expr.Binary(operator=operator, left=expr, right=right)

        return expr

    def parse_logicaland(self) -> Expr:
        expr = self.parse_equality()

        while self.match([TokenKind.AND]):
            operator = self.previous()
            right = self.parse_equality()

            expr = Expr.Binary(operator=operator, left=expr, right=right)

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

            expr = Expr.Binary(operator=operator, left=expr, right=right)

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

            expr = Expr.Binary(operator=operator, left=expr, right=right)

        return expr

    def parse_term(self) -> Expr:
        expr = self.parse_factor()

        while self.match([TokenKind.PLUS, TokenKind.MINUS]):
            operator = self.previous()
            right = self.parse_factor()

            expr = Expr.Binary(operator=operator, left=expr, right=right)

        return expr

    def parse_factor(self) -> Expr:
        expr = self.parse_unary()

        while self.match([TokenKind.STAR, TokenKind.SLASH]):
            operator = self.previous()
            right = self.parse_unary()

            expr = Expr.Binary(operator=operator, left=expr, right=right)

        return expr

    def parse_unary(self):
        if self.match([TokenKind.NOT, TokenKind.MINUS]):
            operator = self.previous()
            right = self.parse_primary()

            return Expr.Unary(operator=operator, right=right)

        return self.parse_call()

    def parse_call(self) -> Expr:
        expr = self.parse_primary()

        while True:
            if self.match([TokenKind.LPAREN]):
                expr = self.finish_call(expr)
                continue

            break

        return expr

    def finish_call(self, calle: Expr) -> Expr:
        paren = self.previous()

        arguments = []
        while True:
            if self.check(kind=TokenKind.RPAREN):
                break

            if len(arguments) > 255:
                raise NeoError(
                    line=self.peek().position.line,
                    message="Can't have more than 255 arguments",
                )

            arguments.append(self.parse_expression())
            if self.match([TokenKind.COMMA]):
                continue

        self.consume(kind=TokenKind.RPAREN, message="Expected ')' after call")
        return Expr.Call(calle=calle, paren=paren, arguments=arguments)

    def parse_primary(self) -> Expr:
        if self.match([TokenKind.TRUE]):
            return Expr.Literal(True)
        if self.match([TokenKind.FALSE]):
            return Expr.Literal(False)
        if self.match([TokenKind.NULL]):
            return Expr.Literal(None)
        if self.match([TokenKind.IDENTIFIER]):
            return Expr.Variable(self.previous())

        if self.match([TokenKind.NUMBER, TokenKind.STRING]):
            return Expr.Literal(self.previous().literal)

        if self.match([TokenKind.LPAREN]):
            expr = self.parse_expression()
            self.consume(kind=TokenKind.RPAREN, message="Expected )")
            return Expr.Grouping(value=expr)

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
