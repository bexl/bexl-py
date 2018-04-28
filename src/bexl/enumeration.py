from six import iteritems


class Enumeration(object):
    @classmethod
    def name_for_value(cls, value):
        for name, val in iteritems(cls.__dict__):
            if value == val:
                return name
        return value

