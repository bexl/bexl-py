from .errors import ParserError
from .lexer import Lexer
from .nodes import Binary, Unary, Literal, Function, Variable, Grouping, \
    List, Indexing, Property
from .token import TokenType
from .types import Types


class Parser(object):
    """
    A parser for BEXL. Parses the output of a lexer and produces an abstract
    syntax tree.

    :param lexer: the Lexer to use when parsing the expression
    :type lexer: bexl.Lexer
    """

    def __init__(self, lexer=Lexer):
        self.lexer = lexer
        self._current = 0
        self._tokens = []

    def _reset(self):
        self._current = 0
        self._tokens = []

    def parse(self, source):
        """
        Parses the source string and returns the corresponding abstract syntax
        tree.

        :param source: the source code to parse
        :type source: str
        :rtype: Expression
        :raises: ParseError if an error occurs during parsing
        """

        self._reset()
        self._tokens = list(self.lexer(source))

        expression = self._expression()

        # If there are still tokens left to parse, then something's wrong.
        if not self._is_at_end():
            token = self._peek()
            raise ParserError(
                'Unexpected token %s' % (
                    token.name,
                ),
                token=token,
            )

        return expression

    def _peek(self):
        return self._tokens[self._current]

    def _is_at_end(self):
        return self._peek().token_type == TokenType.EOF

    def _check(self, token_type):
        if self._is_at_end():
            return False
        return self._peek().token_type == token_type

    def _previous(self):
        return self._tokens[self._current - 1]

    def _advance(self):
        if not self._is_at_end():
            self._current += 1
        return self._previous()

    def _match(self, *args):
        for token_type in args:
            if self._check(token_type):
                self._advance()
                return True
        return False

    def _consume(self, token_type):
        if self._check(token_type):
            return self._advance()
        raise ParserError(
            'Expected token %s' % (
                TokenType.name_for_value(token_type),
            ),
            token=self._peek()
        )

    def _args(self, ending_token):
        arguments = []

        while not self._check(ending_token):
            arguments.append(self._expression())
            if not self._match(TokenType.COMMA):
                break

        self._consume(ending_token)
        return arguments

    def _literal(self):
        if self._match(TokenType.INTEGER):
            return Literal(self._previous(), Types.INTEGER)
        if self._match(TokenType.FLOAT):
            return Literal(self._previous(), Types.FLOAT)
        if self._match(TokenType.STRING):
            return Literal(self._previous(), Types.STRING)
        if self._match(TokenType.FALSE):
            return Literal(self._previous(), Types.BOOLEAN, value=False)
        if self._match(TokenType.TRUE):
            return Literal(self._previous(), Types.BOOLEAN, value=True)
        if self._match(TokenType.NULL):
            return Literal(self._previous(), Types.UNTYPED, value=True)

    def _primary(self):
        literal = self._literal()
        if literal:
            return literal

        if self._match(TokenType.IDENTIFIER):
            identifier = self._previous()
            self._consume(TokenType.LEFT_PAREN)
            args = self._args(TokenType.RIGHT_PAREN)
            end = self._previous()
            return Function(identifier, end, args)

        if self._match(TokenType.LEFT_PAREN):
            start = self._previous()
            expr = self._expression()
            end = self._consume(TokenType.RIGHT_PAREN)
            return Grouping(start, end, expr)

        if self._match(TokenType.LEFT_BRACKET):
            start = self._previous()
            args = self._args(TokenType.RIGHT_BRACKET)
            end = self._previous()
            return List(start, end, args)

        if self._match(TokenType.DOLLAR):
            identifier = self._consume(TokenType.IDENTIFIER)
            return Variable(identifier)

        token = self._peek()
        raise ParserError(
            'Unexpected token %s' % (
                token.name,
            ),
            token=token,
        )

    def _unary(self):
        if self._match(TokenType.BANG, TokenType.MINUS):
            oper = self._previous()
            right = self._unary()
            return Unary(oper, right)

        primary = self._primary()

        while True:
            if self._match(TokenType.LEFT_BRACKET):
                start = end = None

                if self._match(TokenType.COLON):
                    end = self._expression()
                else:
                    start = self._expression()
                    if self._match(TokenType.COLON):
                        if not self._check(TokenType.RIGHT_BRACKET):
                            end = self._expression()
                        else:
                            end = -1

                end_token = self._consume(TokenType.RIGHT_BRACKET)

                primary = Indexing(
                    primary.start_token,
                    end_token,
                    primary,
                    index=start if not end else None,
                    start=start if end else None,
                    end=end if end != -1 else None,
                )

            elif self._match(TokenType.PERIOD):
                identifier = self._consume(TokenType.IDENTIFIER)
                primary = Property(
                    primary.start_token,
                    identifier,
                    primary,
                )

            else:
                break

        return primary

    def _binary(self, term, operators):
        expr = term()

        while self._match(*operators):
            oper = self._previous()
            right = term()
            expr = Binary(expr, oper, right)

        return expr

    def _factor(self):
        return self._binary(
            self._unary,
            (
                TokenType.SLASH,
                TokenType.STAR,
                TokenType.STAR_STAR,
                TokenType.PERCENT,
            ),
        )

    def _term(self):
        return self._binary(
            self._factor,
            (
                TokenType.MINUS,
                TokenType.PLUS,
            ),
        )

    def _comparison(self):
        return self._binary(
            self._term,
            (
                TokenType.EQUAL_EQUAL,
                TokenType.BANG_EQUAL,
                TokenType.LESSER,
                TokenType.LESSER_EQUAL,
                TokenType.GREATER,
                TokenType.GREATER_EQUAL,
            ),
        )

    def _boolean(self):
        return self._binary(
            self._comparison,
            (
                TokenType.AMPERSAND,
                TokenType.PIPE,
                TokenType.CARET,
            ),
        )

    def _expression(self):
        return self._boolean()

