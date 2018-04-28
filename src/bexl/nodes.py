from six import python_2_unicode_compatible


@python_2_unicode_compatible
class Expression(object):
    def accept(self, visitor, **kwargs):
        return getattr(
            visitor,
            'visit_%s' % (self.__class__.__name__.lower(),),
        )(self, **kwargs)

    def pretty(self, indent=0, indent_increment=2):  # noqa: unused-argument,no-self-use
        return u' ' * indent

    def __str__(self):
        return self.pretty()


class Literal(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'data_type',
        'value',
    )

    def __init__(self, token, data_type, value=None):
        self.start_token = self.end_token = token
        self.data_type = data_type
        if value is not None:
            self.value = value
        else:
            self.value = token.literal

    def pretty(self, indent=0, indent_increment=2):
        return u'{indent}{name}({value})'.format(
            indent=u' ' * indent,
            name=self.__class__.__name__,
            value=self.value,
        )


class Unary(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'operator',
        'right',
    )

    def __init__(self, operator, right):
        self.start_token = operator
        self.end_token = right.end_token
        self.operator = operator
        self.right = right

    @property
    def name(self):
        return self.operator.token_type

    def pretty(self, indent=0, indent_increment=2):
        return u'{indent}{name}(\n{inner}{operator},\n{right}\n' \
            '{indent})'.format(
                indent=u' ' * indent,
                inner=u' ' * (indent + indent_increment),
                name=self.__class__.__name__,
                operator=self.operator.name,
                right=self.right.pretty(
                    indent + indent_increment,
                    indent_increment,
                ),
            )


class Binary(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'left',
        'operator',
        'right',
    )

    def __init__(self, left, operator, right):
        self.start_token = left.start_token
        self.end_token = right.end_token
        self.left = left
        self.operator = operator
        self.right = right

    @property
    def name(self):
        return self.operator.token_type

    def pretty(self, indent=0, indent_increment=2):
        return u'{indent}{name}(\n{inner}{operator},\n{left},\n' \
            '{right}\n{indent})'.format(
                indent=u' ' * indent,
                inner=u' ' * (indent + indent_increment),
                name=self.__class__.__name__,
                operator=self.operator.name,
                left=self.left.pretty(
                    indent + indent_increment,
                    indent_increment,
                ),
                right=self.right.pretty(
                    indent + indent_increment,
                    indent_increment,
                ),
            )


class Function(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'arguments',
    )

    def __init__(self, start_token, end_token, arguments):
        self.start_token = start_token
        self.end_token = end_token
        self.arguments = arguments

    @property
    def name(self):
        return self.start_token.lexeme

    def pretty(self, indent=0, indent_increment=2):
        args = [
            u'%s"%s"' % (
                ' ' * (indent + indent_increment),
                self.name,
            ),
        ] + [
            arg.pretty(indent + indent_increment, indent_increment)
            for arg in self.arguments
        ]

        return u'{indent}{name}(\n{args}\n{indent})'.format(
            indent=u' ' * indent,
            name=self.__class__.__name__,
            args=u',\n'.join(args),
        )


class Variable(Expression):
    __slots__ = (
        'start_token',
        'end_token',
    )

    def __init__(self, token):
        self.start_token = self.end_token = token

    @property
    def name(self):
        return self.start_token.lexeme

    def pretty(self, indent=0, indent_increment=2):
        return u'{indent}{name}({variable})'.format(
            indent=u' ' * indent,
            name=self.__class__.__name__,
            variable=self.name,
        )


class Grouping(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'expression',
    )

    def __init__(self, start_token, end_token, expression):
        self.start_token = start_token
        self.end_token = end_token
        self.expression = expression

    def pretty(self, indent=0, indent_increment=2):
        return u'{indent}{name}(\n{expr}\n{indent})'.format(
            indent=u' ' * indent,
            name=self.__class__.__name__,
            expr=self.expression.pretty(
                indent + indent_increment,
                indent_increment,
            ),
        )


class List(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'elements',
    )

    def __init__(self, start_token, end_token, elements):
        self.start_token = start_token
        self.end_token = end_token
        self.elements = elements

    def pretty(self, indent=0, indent_increment=2):
        return u'{indent}{name}(\n{elements}\n{indent})'.format(
            indent=u' ' * indent,
            name=self.__class__.__name__,
            elements=u',\n'.join([
                elem.pretty(indent + indent_increment)
                for elem in self.elements
            ]),
        )


class Indexing(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'expression',
        'start',
        'end',
    )

    def __init__(
            self,
            start_token,
            end_token,
            expression,
            index=None,
            start=None,
            end=None):
        self.start_token = start_token
        self.end_token = end_token
        self.expression = expression
        self.index = index
        self.start = start
        self.end = end

    def pretty(self, indent=0, indent_increment=2):
        if self.index is not None:
            loc = self.index.pretty(
                indent + indent_increment,
                indent_increment,
            )
        else:
            inner = u' ' * (indent + indent_increment)
            null = inner + (u' ' * indent_increment) + 'null'
            loc = u'{inner}(\n{start},\n{end}\n{inner})'.format(
                inner=inner,
                start=self.start.pretty(
                    indent + (indent_increment * 2),
                    indent_increment,
                ) if self.start else null,
                end=self.end.pretty(
                    indent + (indent_increment * 2),
                    indent_increment,
                ) if self.end else null,
            )
        return u'{indent}{name}(\n{expr},\n{loc}\n{indent})'.format(
            indent=u' ' * indent,
            name=self.__class__.__name__,
            expr=self.expression.pretty(
                indent + indent_increment,
                indent_increment,
            ),
            loc=loc,
        )


class Property(Expression):
    __slots__ = (
        'start_token',
        'end_token',
        'expression',
    )

    def __init__(self, start_token, end_token, expression):
        self.start_token = start_token
        self.end_token = end_token
        self.expression = expression

    @property
    def name(self):
        return self.end_token.lexeme

    def pretty(self, indent=0, indent_increment=2):
        return u'{indent}{name}(\n{inner}"{prop}",\n{expr}\n{indent})'.format(
            indent=u' ' * indent,
            inner=u' ' * (indent + indent_increment),
            name=self.__class__.__name__,
            expr=self.expression.pretty(
                indent + indent_increment,
                indent_increment,
            ),
            prop=self.name,
        )

