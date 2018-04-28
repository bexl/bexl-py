from six import text_type

from .errors import LexerError
from .token import Token, TokenType


TOKEN_MAP = {
    '+': {
        None: TokenType.PLUS,
    },
    '-': {
        None: TokenType.MINUS,
    },
    '/': {
        None: TokenType.SLASH,
    },
    '%': {
        None: TokenType.PERCENT,
    },
    '&': {
        None: TokenType.AMPERSAND,
    },
    '|': {
        None: TokenType.PIPE,
    },
    '^': {
        None: TokenType.CARET,
    },
    '(': {
        None: TokenType.LEFT_PAREN,
    },
    ')': {
        None: TokenType.RIGHT_PAREN,
    },
    '[': {
        None: TokenType.LEFT_BRACKET,
    },
    ']': {
        None: TokenType.RIGHT_BRACKET,
    },
    ',': {
        None: TokenType.COMMA,
    },
    '$': {
        None: TokenType.DOLLAR,
    },
    ':': {
        None: TokenType.COLON,
    },
    '.': {
        None: TokenType.PERIOD,
    },
    '*': {
        '*': {
            None: TokenType.STAR_STAR,
        },
        None: TokenType.STAR,
    },
    '!': {
        '=': {
            None: TokenType.BANG_EQUAL,
        },
        None: TokenType.BANG,
    },
    '<': {
        '=': {
            None: TokenType.LESSER_EQUAL,
        },
        None: TokenType.LESSER,
    },
    '>': {
        '=': {
            None: TokenType.GREATER_EQUAL,
        },
        None: TokenType.GREATER,
    },
}

KEYWORD_TOKENS = {
    'True': TokenType.TRUE,
    'False': TokenType.FALSE,
    'Null': TokenType.NULL,
}


class Lexer(object):
    """
    A lexical analyzer for BEXL. Parses a string and produces a sequence of
    Tokens.

    :param source: the BEXL expression to lex
    :type source: str
    """

    def __init__(self, source):
        self.source = source
        self._start = 0
        self._current = 0
        self._line = 0
        self._line_start = 0
        self._ended = False

    def __iter__(self):
        self._reset()
        return self

    def __next__(self):
        if self._ended:
            raise StopIteration()

        token = self._scan_token()
        while token is None:
            token = self._scan_token()

        return token

    next = __next__

    def lex(self):
        """
        Parses the source string and returns the Tokens it contains.

        :rtype: list of Token
        :raises: LexerError if an error occurs during parsing
        """

        return list(self)

    def _reset(self):
        self._start = 0
        self._current = 0
        self._line = 0
        self._line_start = 0
        self._ended = False

    def _scan_token(self):  # noqa: too-many-return-statements
        self._start = self._current
        if self._is_at_end():
            self._ended = True
            return self._make_token(TokenType.EOF)

        char = self._advance()

        if char in TOKEN_MAP:
            return self._make_token(self._find_in_map(TOKEN_MAP[char]))

        if char == '=' and self._match('='):
            return self._make_token(TokenType.EQUAL_EQUAL)

        if char in [' ', '\r', '\t', '\v']:
            return None

        if char == '\n':
            self._line += 1
            self._line_start = self._current
            return None

        if char == "'":
            return self._string()

        if self._is_digit(char):  # or char == '.':
            return self._number()

        if self._is_alpha(char):
            return self._identifier()

        raise self._make_error('Unexpected character "%s"' % (char,))

    def _find_in_map(self, tmap):
        if len(tmap) == 1:
            return tmap[None]
        char = self._peek()
        if char is not None and char in tmap:
            return self._find_in_map(tmap[self._advance()])
        return tmap[None]

    def _make_token(
            self,
            token_type,
            literal=None,
            line=None,
            column=None,
            length=None):
        if token_type != TokenType.EOF:
            text = self.source[self._start:self._current]
        else:
            text = None

        if line is None:
            line = self._line

        if column is None:
            column = self._start - self._line_start

        if length is None:
            if literal is None:
                length = self._current - self._start
            else:  # pragma: no cover
                length = len(literal)

        return Token(token_type, text, literal, line, column, length)

    def _make_error(self, message):
        raise LexerError(
            message,
            line=self._line,
            column=self._start - self._line_start,
        )

    def _string(self):
        line = self._line
        column = self._current - 1

        while not self._is_at_end() and not self._peek() == "'":
            char = self._advance()

            if char == '\\':
                if self._peek() == "'":
                    self._advance()

            elif char == '\n':
                self._line += 1
                self._line_start = self._current + 1

        if self._is_at_end():
            raise self._make_error('Unterminated string literal')

        self._advance()
        value = self.source[(self._start + 1):(self._current - 1)]
        length = len(value) + 2
        value = value.replace("\\'", "'")

        return self._make_token(
            TokenType.STRING,
            literal=text_type(value),
            line=line,
            column=column,
            length=length,
        )

    def _number(self):
        have_decimal = self._peek(0) == '.'

        while self._is_digit(self._peek()):
            self._advance()

        if not have_decimal \
                and self._peek() == '.' \
                and self._is_digit(self._peek(2)):
            have_decimal = True
            self._advance()
            while self._is_digit(self._peek()):
                self._advance()

        if self._peek() in ('e', 'E'):
            after = self._peek(2)
            if after in ('-', '+') or self._is_digit(after):
                self._advance(2)
                while self._is_digit(self._peek()):
                    self._advance()
            else:
                raise self._make_error('Incomplete float literal')

        lexeme = self.source[self._start:self._current].lower()
        if 'e' in lexeme or '.' in lexeme:
            return self._make_token(
                TokenType.FLOAT,
                literal=float(lexeme),
                length=len(lexeme),
            )

        return self._make_token(
            TokenType.INTEGER,
            literal=int(lexeme),
            length=len(lexeme),
        )

    def _identifier(self):
        while self._is_identifier_character(self._peek()):
            self._advance()
        text = self.source[self._start:self._current]
        return self._make_token(KEYWORD_TOKENS.get(text, TokenType.IDENTIFIER))

    def _is_digit(self, char):  # noqa: no-self-use
        char = char or ''
        return '0' <= char <= '9'

    def _is_alpha(self, char):  # noqa: no-self-use
        char = char or ''
        return ('a' <= char <= 'z') \
            or ('A' <= char <= 'Z')

    def _is_alpha_numeric(self, char):
        return self._is_alpha(char) or self._is_digit(char)

    def _is_identifier_character(self, char):
        return char == '_' or self._is_alpha_numeric(char)

    def _is_at_end(self):
        return self._current >= len(self.source)

    def _match(self, char):
        if self._peek() == char:
            self._advance()
            return True
        return False

    def _peek(self, depth=1):
        pos = self._current + (depth - 1)
        if pos >= len(self.source):
            return None
        return self.source[pos]

    def _advance(self, depth=1):
        self._current += depth
        return self.source[self._current - 1]

