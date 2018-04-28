from six import python_2_unicode_compatible

from .enumeration import Enumeration


@python_2_unicode_compatible
class Token(object):
    __slots__ = (
        'token_type',
        'lexeme',
        'literal',
        'line',
        'column',
        'length',
    )

    def __init__(self, token_type, lexeme, literal, line, column, length):
        self.token_type = token_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
        self.column = column
        self.length = length

    @property
    def name(self):
        return TokenType.name_for_value(self.token_type)

    def pretty(self, indent=0, indent_increment=2):  # noqa: unused-argument
        return u'{indent}{name}({line}:{column}, {type}, {value})'.format(
            indent=u' ' * indent,
            name=self.__class__.__name__,
            line=self.line,
            column=self.column,
            type=TokenType.name_for_value(self.token_type),
            value=repr(self.lexeme if self.literal is None else self.literal),
        )

    def __str__(self):
        return self.pretty()


class TokenType(Enumeration):
    PLUS = '+'
    MINUS = '-'
    STAR = '*'
    SLASH = '/'
    PERCENT = '%'
    STAR_STAR = '**'
    EQUAL_EQUAL = '=='
    BANG_EQUAL = '!='
    LESSER = '<'
    LESSER_EQUAL = '<='
    GREATER = '>'
    GREATER_EQUAL = '>='
    AMPERSAND = '&'
    PIPE = '|'
    CARET = '^'
    BANG = '!'
    LEFT_PAREN = '('
    RIGHT_PAREN = ')'
    LEFT_BRACKET = '['
    RIGHT_BRACKET = ']'
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    NULL = 'NULL'
    IDENTIFIER = 'IDENTIFIER'
    COMMA = ','
    DOLLAR = '$'
    COLON = ':'
    PERIOD = '.'
    EOF = 'EOF'

