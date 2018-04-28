import argparse
import codecs
import datetime
import os
import readline
import sys
import textwrap

import pkg_resources

from six import text_type, string_types, print_, iteritems
from six.moves import input as get_input

from .errors import BexlError, LexerError, ParserError, InterpreterError
from .interpreter import Interpreter
from .lexer import Lexer
from .parser import Parser
from .resolver import VariableResolver
from .types import DateValue, TimeValue, DateTimeValue, StringValue


def attempt_variable_coercion(value):
    if value.lower() == 'true':
        value = True
    elif value.lower() == 'false':
        value = False
    elif DateValue.REGEX.match(value):
        value = DateValue.from_value(StringValue(value)).value
    elif TimeValue.REGEX.match(value):
        value = TimeValue.from_value(StringValue(value)).value
    elif DateTimeValue.REGEX.match(value):
        value = DateTimeValue.from_value(StringValue(value)).value
    else:
        try:
            value = float(value)
        except ValueError:
            pass
        else:
            if value.is_integer():
                value = int(value)
    return value


class Repl(object):
    def __init__(self):
        self.debug = False
        self.resolver = VariableResolver()
        self.parser = argparse.ArgumentParser(
            description='Evaluates Basic EXpression Language (BEXL)'
            ' expressions.',
        )

        try:
            self.version = \
                pkg_resources.get_distribution('bexl').version
        except pkg_resources.DistributionNotFound:
            self.version = 'UNKNOWN'
        self.version = 'bexl-py ' + self.version

        self.parser.add_argument(
            '-v',
            '--version',
            action='version',
            version=self.version,
        )

        self.parser.add_argument(
            'source_file',
            action='store',
            nargs='?',
            default=None,
            help='the path to the file containing a BEXL expression to'
            ' evaluate',
        )

        self.parser.add_argument(
            '-e',
            '--eval',
            action='store',
            metavar='EXPR',
            help='evaluates the specified BEXL expression and outputs the'
            ' result',
        )
        self.parser.add_argument(
            '-d',
            '--debug',
            action='store_true',
            help='enables debug mode, which outputs parsing and evaluation in'
            ' addition to the results',
        )

        self.parser.add_argument(
            '--var',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets a variable for use in the expression',
        )
        self.parser.add_argument(
            '--intvar',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets an integer variable for use in the expression',
        )
        self.parser.add_argument(
            '--floatvar',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets a float variable for use in the expression',
        )
        self.parser.add_argument(
            '--boolvar',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets a boolean variable for use in the expression',
        )
        self.parser.add_argument(
            '--strvar',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets a string variable for use in the expression',
        )
        self.parser.add_argument(
            '--datevar',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets a date variable for use in the expression',
        )
        self.parser.add_argument(
            '--timevar',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets a time variable for use in the expression',
        )
        self.parser.add_argument(
            '--datetimevar',
            action='append',
            metavar='NAME=VALUE',
            default=[],
            help='sets a datetime variable for use in the expression',
        )

    def __call__(self, argv):
        args = self.parse_arguments(argv)

        if args.eval:
            return 0 if self.run_source(args.eval) else 1

        if args.source_file:
            with codecs.open(args.source_file, 'r', encoding='utf-8') as sfile:
                source = sfile.read()
            return 0 if self.run_source(source) else 1

        print_(self.version)
        print_('Type \\h for help')
        readline.parse_and_bind('set enable-keypad on')
        readline.parse_and_bind('set editing-mode vi')
        readline.parse_and_bind('set blink-matching-paren on')
        readline.parse_and_bind('set history-size 100')
        history_file = os.path.expanduser('~/.bexl_history')
        if os.path.exists(history_file):
            readline.read_history_file(history_file)

        try:
            while True:
                source = get_input('> ')
                if source.startswith('\\'):
                    self.do_command(source)
                elif source:
                    self.run_source(source)
        except (KeyboardInterrupt, EOFError):
            print_('')
            return 1
        finally:
            readline.write_history_file(history_file)

    def die(self, message):  # noqa: no-self-use
        print_(message)
        sys.exit(1)

    def parse_arguments(self, argv):
        args = self.parser.parse_args(argv)

        self.debug = args.debug

        variables = (
            ('', None, args.var),
            ('integer', int, args.intvar),
            ('float', float, args.floatvar),
            ('boolean', bool, args.boolvar),
            ('string', string_types, args.strvar),
            ('date', datetime.date, args.datevar),
            ('time', datetime.time, args.timevar),
            ('datetime', datetime.datetime, args.datetimevar),
        )

        for description, type_check, specified_vars in variables:
            for var in specified_vars:
                parts = var.split('=', 1)
                if len(parts) == 2:
                    value = attempt_variable_coercion(parts[1])
                    if type_check and not isinstance(value, type_check):
                        self.die(
                            'Invalid %s specified: %s' % (description, var)
                        )
                    self.resolver[parts[0]] = value
                else:
                    self.resolver[var] = None

        return args

    def run_source(self, source):  # noqa: @mccabe
        if self.debug:
            try:
                tokens = list(Lexer(source))
            except BexlError as exc:
                self.show_error(source, exc)
                return False
            else:
                print_('Tokens Found:')
                for token in tokens:
                    print_(token.pretty(2))
                print_('')

        try:
            tree = Parser().parse(source)
            if self.debug:
                print_('AST:')
                print_(tree.pretty(indent=2))
                print_('')
        except BexlError as exc:
            self.show_error(source, exc)
            return False

        try:
            result = Interpreter().interpret(
                tree,
                variable_resolver=self.resolver,
            )
            if self.debug:
                print_('Result:')
                print_('  %r' % (result,))
                print_('')
        except BexlError as exc:
            self.show_error(source, exc)
            return False
        else:
            output = text_type(result)
            if isinstance(output, list):
                output = '[%s]' % (
                    ', '.join([
                        text_type(value)
                        for value in output
                    ])
                )
            print_(output)
            return True

    def show_error(self, source, error):  # noqa: no-self-use
        print_('Error: %s' % (error,))
        print_(source)

        if isinstance(error, LexerError):
            start = error.column
            end = error.column
        elif isinstance(error, ParserError):
            start = error.token.column
            end = start + error.token.length
        elif isinstance(error, InterpreterError):
            start = error.node.start_token.column
            end = error.node.end_token.column + error.node.end_token.length

        location = ' ' * start
        location += '^' * ((end - start) or 1)
        print_(location)

    def do_command(self, command):
        parts = command.split(' ')
        cmd = getattr(self, 'cmd_%s' % (parts[0][1:],), None)
        if cmd:
            cmd(parts[1:])
        else:
            print_('Unrecognized command: %s' % (command,))

    def cmd_d(self, args):
        """
        \\d [on|off]
            Enables or disables debug mode.
        """

        if not args:
            print_('Debug mode is %s' % ('ON' if self.debug else 'OFF'))

        elif args[0].lower() == 'on':
            self.debug = True

        elif args[1].lower() == 'off':
            self.debug = False

    def cmd_v(self, args):
        """
        \\v [name] [value]
            Sets the variable [name] so that it can be used in expressions. If
            no [value] is provided, prints the value of the specified variable.
            If no [name] is provided, lists all variables and their values.
        """

        if not args:
            for key, value in iteritems(self.resolver):
                print_(u'%s = %r' % (key, value))

        else:
            if len(args) == 1:
                value = self.resolver.get(args[0], None)
                if value:
                    print_(u'%s = %r' % (args[0], value))

            else:
                name = args[0]
                value = ' '.join(args[1:])
                self.resolver[name] = attempt_variable_coercion(value)

    def _cmd_v(self, description, type_check, args):
        if not args:
            pass

        elif len(args) == 1:
            value = self.resolver.get(args[0], None)
            if value:
                print_(u'%s = %s' % (args[0], value))

        else:
            name = args[0]
            value = attempt_variable_coercion(' '.join(args[1:]))
            if not isinstance(value, type_check):
                print_('"%s" is not a %s value' % (value, description))
            else:
                self.resolver[name] = value

    def cmd_vi(self, args):
        """
        \\vi <name> [value]
            Sets an integer variable <name> so that it can be used in
            expressions. If no [value] is provided, prints the value of the
            specified variable.
        """

        self._cmd_v('integer', int, args)

    def cmd_vf(self, args):
        """
        \\vf <name> [value]
            Sets a float variable <name> so that it can be used in expressions.
            If no [value] is provided, prints the value of the specified
            variable.
        """

        self._cmd_v('float', float, args)

    def cmd_vb(self, args):
        """
        \\vb <name> [value]
            Sets a boolean variable <name> so that it can be used in
            expressions. If no [value] is provided, prints the value of the
            specified variable.
        """

        self._cmd_v('boolean', bool, args)

    def cmd_vs(self, args):
        """
        \\vs <name> [value]
            Sets a string variable <name> so that it can be used in
            expressions. If no [value] is provided, prints the value of the
            specified variable.
        """

        self._cmd_v('string', string_types, args)

    def cmd_vd(self, args):
        """
        \\vd <name> [value]
            Sets a date variable <name> so that it can be used in expressions.
            If no [value] is provided, prints the value of the specified
            variable.
        """

        self._cmd_v('date', datetime.date, args)

    def cmd_vt(self, args):
        """
        \\vt <name> [value]
            Sets a time variable <name> so that it can be used in expressions.
            If no [value] is provided, prints the value of the specified
            variable.
        """

        self._cmd_v('time', datetime.time, args)

    def cmd_vdt(self, args):
        """
        \\vdt <name> [value]
            Sets a datetime variable <name> so that it can be used in
            expressions. If no [value] is provided, prints the value of the
            specified variable.
        """

        self._cmd_v('datetime', datetime.datetime, args)

    def cmd_vx(self, args):
        """
        \\vx <name>
            Deletes the variable [name].
        """

        if not args or args[0] not in self.resolver:
            return
        del self.resolver[args[0]]

    def cmd_q(self, args):  # noqa: no-self-use,unused-argument
        """
        \\q
            Quits this interpreter session.
        """

        raise EOFError()

    def cmd_h(self, args):  # noqa: unused-argument
        for attr in sorted(dir(self)):
            if not attr.startswith('cmd_'):
                continue
            cmd = getattr(self, attr)
            if not cmd.__doc__:
                continue
            print_(textwrap.dedent(cmd.__doc__[1:]))


def main():
    Repl()(sys.argv[1:])

