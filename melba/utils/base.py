
from datetime import datetime
from urlparse import urlparse

try:
    from configparser import ConfigParser as BaseParser, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser as BaseParser, NoOptionError
    from ast import literal_eval

from slugify import slugify

__all__ = [
    'import_object',
    'String',
    'slugify',
    'slugify_vcs_url',
    'evaluate_config_options',
    'ConfigParser',
    'NoOptionError',
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

def slugify_vcs_url(url):
    path = urlparse(url).path
    scheme, at, path = path.partition('@')
    if not at:
        path = scheme
    return slugify(path)

class Python2Parser(BaseParser):

    def _interpolate(self, section, option, rawval, vars):
        try:
            return literal_eval(rawval)
        except:
            return ''

def ConfigParser():
    try:
        import configparser
    except ImportError:
        return Python2Parser()
    else:
        from .typedinterpolation import TypedBasicInterpolation
        return BaseParser(interpolation=TypedBasicInterpolation)

def evaluate_config_options(cfg, section):
    options = {}
    settings = {}
    for k, v in cfg.items(section):
        if k == k.lower():
            options[k] = v
        elif k == k.upper():
            settings[k] = v
    return options, settings

