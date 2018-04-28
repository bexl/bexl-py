import pytest

from bexl import Lexer, LexerError, Parser, ParserError, Interpreter, InterpreterError


LEXER_ERRORS = (
    'foo=#',  # unexpected character
    "'foo",  # unterminated string
    "123e",  # incomplete float
)

@pytest.mark.parametrize('source', LEXER_ERRORS)
def test_lexer_errors(source):
    with pytest.raises(LexerError):
        tokens = Lexer(source).lex()


PARSER_ERRORS = (
    '1]',  # unexpected token
    'foo(',  # unexpected token
    'foo(1',  # missing token
)

@pytest.mark.parametrize('source', PARSER_ERRORS)
def test_parser_errors(source):
    with pytest.raises(ParserError):
        tree = Parser().parse(source)


INTERPRETER_ERRORS = (
    '$test',
    "record('foo', 123).bar",
    '!12',
    '123[1]',
    '123[1:2]',
    "'foo'+123",
    'doesntexist()',
)

@pytest.mark.parametrize('source', INTERPRETER_ERRORS)
def test_interpreter_errors(source):
    with pytest.raises(InterpreterError):
        result = Interpreter().interpret(Parser().parse(source))

