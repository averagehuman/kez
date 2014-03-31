
from datetime import datetime

__all__ = [
    'import_object',
    'String',
]

def import_object(name):
    """Imports an object by name.

    import_object('x.y.z') is equivalent to 'from x.y import z'.

    """
    name = str(name)
    if '.' not in name:
        return __import__(name)
    parts = name.split('.')
    m = '.'.join(parts[:-1])
    attr = parts[-1]
    obj = __import__(m, None, None, [attr], 0)
    try:
        return getattr(obj, attr)
    except AttributeError, e:
        raise ImportError("'%s' does not exist in module '%s'" % (attr, m))


class String(object):
    TIME_FORMAT = '%H:%M:%S.%f'
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    @staticmethod
    def parse_time(s):
        return datetime.strptime(s, TIME_FORMAT)

    @staticmethod
    def parse_date(s):
        return datetime.strptime(s, DATE_FORMAT)

    @staticmethod
    def parse_datetime(s):
        return datetime.strptime(s, DATETIME_FORMAT)

    @staticmethod
    def format_time(dt):
        return datetime.strftime(dt, TIME_FORMAT)

    @staticmethod
    def format_date(dt):
        return datetime.strftime(dt, DATE_FORMAT)

    @staticmethod
    def format_datetime(dt):
        return datetime.strftime(dt, DATETIME_FORMAT)


