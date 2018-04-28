
class BexlError(Exception):
    """
    Base exception that all bexl-generated exceptions inherits from.
    """


class LexerError(BexlError):
    """
    Represents an error that occured during the lexical analysis of the
    provided source code.
    """

    def __init__(self, *args, **kwargs):
        self.line = kwargs.pop('line', None)
        self.column = kwargs.pop('column', None)
        super(LexerError, self).__init__(*args, **kwargs)


class ParserError(BexlError):
    """
    Represents an error that occurred during the parsing of the tokens in the
    provided source code.
    """

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token', None)
        super(ParserError, self).__init__(*args, **kwargs)

    @property
    def line(self):
        return self.token.line if self.token else None

    @property
    def column(self):
        return self.token.column if self.token else None


class InterpreterError(BexlError):
    """
    Represents an error that occurred during the interpreting of the abstract
    syntax tree in the provided source code.
    """

    def __init__(self, *args, **kwargs):
        self.node = kwargs.pop('node', None)
        super(InterpreterError, self).__init__(*args, **kwargs)


class ResolverError(InterpreterError):
    """
    Represents an error that occurred during the resolution of a variable name.
    """


class DispatchError(InterpreterError):
    """
    Represents an error that occurred while trying to find the appropriate
    implementation of an operator or function to execute.
    """


class ExecutionError(InterpreterError):
    """
    Represents an error that occurred during the execution of the interpreted
    abstract syntax tree in the provided source code.
    """


class ConversionError(InterpreterError):
    """
    Represents an error that occurred while trying to convert a value of one
    type into another.
    """

    def __init__(self, *args, **kwargs):
        self.value = kwargs.pop('value', None)
        self.target_type = kwargs.pop('target_type', None)
        super(ConversionError, self).__init__(*args, **kwargs)

