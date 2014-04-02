"""

"""
import sys
import os
from copy import copy as shallow_copy
from optparse import make_option
from codecs import open
from itertools import chain
import tempfile
import ConfigParser
from os.path import join as pathjoin, exists as pathexists
from ast import literal_eval

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ImproperlyConfigured
from django.template import loader, Context
from django.conf import settings

from pelican import Pelican, main, generators, writers, settings as pelican_settings
from pelican.readers import Readers
from pelican import signals

from bigmouth.utils import get_flatpage_root

# items from Django settings that we want to add to the Pelican template context
CONTEXT_PARAMS = set([
    'STATIC_URL', 'MEDIA_URL', 'DEBUG', 'TEMPLATE_DEBUG',
    'COMPRESS_ENABLED',
])
BINARY_EXTENSIONS = set([
    '.jpeg', '.jpg', '.png', '.ico', '.gif',
    '.pdf', '.doc', '.docx', '.xls',
])

def update_context(cfg):
    for var in CONTEXT_PARAMS:
        cfg[var] = getattr(settings, var, None)

class AltContext(Context):
    """
    A Django Context object does not have the 'copy' method that pelican
    expects, but it does support shallow copying (ie. has a __copy__ method)
    """

    def copy(self):
        return shallow_copy(self)

class AltGenerator(generators.Generator):
    """
    Subclass of the base pelican Generator class without the Jinja setup.

    This works because pelican only cares that a template object has a method
    called `render` and that it returns a string.
    """

    def __init__(self, context, settings, path, theme, output_path, **kwargs):
        update_context(context)
        self.context = AltContext(context)
        self.settings = settings
        self.path = path
        self.theme = theme
        self.output_path = output_path

        for arg, value in kwargs.items():
            setattr(self, arg, value)

        self.readers = Readers(self.settings)
        signals.generator_init.send(self)

#    def __init__(self, *args, **kwargs):
#        for idx, item in enumerate(
#            ('context', 'settings', 'path', 'theme', 'output_path')):
#            if idx == 0:
#                cfg = args[idx]
#                update_context(cfg)
#                setattr(self, item, AltContext(cfg))
#            else:
#                setattr(self, item, args[idx])
#        for arg, value in kwargs.items():
#            setattr(self, arg, value)

    def get_template(self, name):
        return loader.get_template('bigmouth/' + name + '.html')

class AltWriter(writers.Writer):
    """
    A Writer class that writes each file as an index.html in its own directory.
    This requires that templates are updated with the correct urls, eg.

        /blog/first-post.html  -->  /blog/first-post/

    """

    def write_file(self, name, template, context, relative_urls=True,
        paginated=None, **kwargs):
        if not name.endswith('index.html'):
            name = os.path.splitext(name)[0].rstrip('/') + '/index.html'
        super(AltWriter, self).write_file(
            name, template, context, relative_urls, paginated, **kwargs
        )

class ArticlesGenerator(generators.ArticlesGenerator, AltGenerator):
    """Generate blog articles"""

    def __init__(self, *args, **kwargs):
        super(ArticlesGenerator, self).__init__(*args, **kwargs)

class PagesGenerator(generators.PagesGenerator, AltGenerator):
    """Generate pages"""

    def __init__(self, *args, **kwargs):
        super(PagesGenerator, self).__init__(*args, **kwargs)

class StaticGenerator(generators.StaticGenerator, AltGenerator):
    """copy static paths (what you want to cpy, like images, medias etc.
    to output"""

    def __init__(self, *args, **kwargs):
        super(StaticGenerator, self).__init__(*args, **kwargs)

class Cormorant(Pelican):
    """
    Subclass of the Pelican application class. The management command below
    will ultimately kick off the `Pelican.run` method which itself invokes a
    list of generators to do the heavy lifting; this subclass ensures that the
    generators are our own "Django Inside!" versions.
    """
    
    def get_generator_classes(self):
        generator_list = [ArticlesGenerator, PagesGenerator]#, StaticGenerator]
        return generator_list

    def get_writer(self):
        return AltWriter(self.output_path, settings=self.settings)

class Command(BaseCommand):
    """Generate a Pelican blog and save files both to the filesystem and as Django flatpages.

    Example usage::

        python manage.py run_pelican -o deploy-site/blog/ static/blog
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '-s',
            '--site',
            dest='site',
            type='string',
            help='when there are multiple source documents within the same'
                'directory or repository, select which document/site to build.'),
        make_option(
            '-t',
            '--theme-path',
            dest='theme',
            type='string',
            help='where to find the theme templates. If not specified, it'
                'will use the default theme included with pelican.'),
        make_option(
            '-o',
            '--output',
            dest='output',
            type='string',
            help='Where to output the generated files. If not specified, a directory'
                ' will be created, named "output" in the current path.'),
        make_option(
            '-m',
            '--markup',
            dest='markup',
            type='string',
            help='the list of markup language to use (rst or md). Please indicate '
                'them separated by commas'),
        make_option(
            '-D',
            '--debug',
            dest='debug',
            action='store_true',
            default=False,
            help='show debug messages'),
        make_option(
            '-x',
            '--no-flatpages',
            dest='flatpages',
            action="store_false",
            default=True,
            help="don't create a Django flatpage for every blog page"),
    )

    def get_repo(self, url):
        from gravy import anyrepo
        repo = anyrepo(url)
        for i in range(3):
            try:
                repo.pull(update=True)
            except:
                if i == 2:
                    raise
                continue
            else:
                break
        return repo

    def default_settings(self):
        return dict(
            ARTICLE_URL = '{date:%Y}/{date:%m}/{slug}/',
            ARTICLE_LANG_URL = '{date:%Y}/{date:%m}/{lang}/{slug}/',
            PAGE_URL = '{slug}/',
            PAGE_LANG_URL = '{lang}/{slug}/',
            ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{slug}/index.html',
            ARTICLE_LANG_SAVE_AS = '{lang}/{date:%Y}/{date:%m}/{slug}/index.html',
            PAGE_SAVE_AS = '{slug}/index.html',
            PAGE_LANG_SAVE_AS = '{lang}/{slug}/index.html',
            TIMEZONE = 'Europe/London',
            FEED_MAX_ITEMS = 100,
            FEED_ALL_RSS = 'feeds/all.rss',
            CATEGORY_FEED_RSS = 'feeds/category/%s.rss',
            TRANSLATION_FEED_RSS = 'feeds/lang/all-%s.rss',
            FEED_ALL_ATOM = 'feeds/all.atom',
            CATEGORY_FEED_ATOM = 'feeds/category/%s.atom',
            TRANSLATION_FEED_ATOM = 'feeds/lang/all-%s.atom',
        )

    def fixed_settings(self):
        return ((key, str(val)) for key, val in (
            #('PELICAN_CLASS', 'bigmouth.management.commands.run_pelican.Cormorant'),
            ('PELICAN_CLASS', 'bigmouth.Cormorant'),
            ('DELETE_OUTPUT_DIRECTORY', False),
            ('PDF_GENERATOR', False),
            ('PLUGINS', [
                'bigmouth.plugins.ipython',
                'bigmouth.plugins.neighbors',
                'bigmouth.plugins.multi_part',
                'bigmouth.plugins.html_rst_directive',
            ]),
        ))

    def validate_settings(self, options):
        options.setdefault('SITEURL', '')
        options.setdefault('FEED_DOMAIN', options['SITEURL'])

    def generate_settings_file(self, source_root, site=None):
        userfile = pathjoin(source_root, 'bigmouth.cfg')
        overrides = {}
        if pathexists(userfile):
            cfg = ConfigParser.ConfigParser()
            try:
                with open(userfile) as fp:
                    cfg.readfp(fp)
            except:
                self.stderr.write("unable to read user config file")
            else:
                try:
                    overrides = dict((k.upper(), v) for k,v in cfg.items(site))
                except ConfigParser.NoSectionError:
                    # no site given or a bad site name
                    # in either case, if there is a single section, then use it
                    # otherwise use the default section
                    sections = cfg.sections()
                    if len(sections) == 1:
                        overrides = dict((k.upper(), v) for k,v in cfg.items(sections[0]))
                    else:
                        overrides = dict((k.upper(), v) for k,v in cfg.defaults().items())
        options = self.default_settings()
        # update configurable options
        options.update(overrides) 
        # update non-configurable options
        options.update(self.fixed_settings())
        self.validate_settings(options)
        settingsfile = pathjoin(
            tempfile.mkdtemp(prefix='bigmouth-', suffix='-'+os.path.basename(source_root)),
            'settings.py'
        )
        with open(settingsfile, 'w') as settings:
            settings.write('\n')
            # we are writing a python settings file based on user entered data
            # and so must ensure that everything being written is not runnable code
            for key, val in options.items():
                try:
                    val = literal_eval(val)
                except:
                    try:
                        if '"' in val:
                            val = "'" + val + "'"
                        else:
                            val = '"' + val + '"'
                        val = literal_eval(val)
                    except:
                        val = ''
                settings.write('%s = %s\n' % (key.upper(), repr(val)))
            settings.write('\n')
        return settingsfile

    def handle(self, *args, **options):
        if not args:
            raise CommandError("A content source directory (or remote repository) was not given.")
        if not options['output']:
            raise CommandError("An output directory was not given.")
        sources = args[0]
        if '://' in sources:
            sources = self.get_repo(sources).path
        sources = sources.rstrip('/')
        #cfg = os.path.splitext(
        #    sys.modules[os.environ['DJANGO_SETTINGS_MODULE']].__file__
        #)[0] + '.py'
        #assert os.path.exists(cfg)
        site = options.get('site', None)
        cfg = self.generate_settings_file(sources, site)
        cfgdir = os.path.dirname(cfg)
        argv = [
            'pelican',
            '--settings=%s' % cfg,
            '--verbose',
            '--output=%s' % options['output'],
        ]
        if options['markup']:
            argv.append('--markup=%s' % options['markup'])
        if options['theme']:
            argv.append('--theme-path=%s' % options['theme'])
        if options['debug']:
            argv.append('--debug')
        argv.append(sources)
        sys.argv[:] = argv
        # use our own Pelican subclass
        pelican_settings.DEFAULT_CONFIG['PELICAN_CLASS'] = Cormorant
        try:
            main()
        finally:
            pass#os.rmdir(cfgdir)
        if options['flatpages']:
            from django.contrib.flatpages.models import FlatPage
            outdir = options['output'].rstrip(os.sep)
            url_prefix = get_flatpage_root()
            query = FlatPage.objects.filter(
                sites__id=settings.SITE_ID
            ).filter(
                url__startswith=url_prefix
            )
            # delete existing flatpages
            query.delete()
            for root, dirs, files in os.walk(outdir):
                for f in files:
                    ext= os.path.splitext(f)[1]
                    if ext.lower() in BINARY_EXTENSIONS:
                        continue
                    filename = os.path.join(root, f)
                    url = url_prefix + filename[len(outdir)+1:]
                    if url.endswith('/index.html'):
                        url = url[:-10]
                    with open(filename, encoding='utf-8' ) as fileobj:
                        try:
                            s = fileobj.read()
                            page = FlatPage.objects.create(
                                url=url, title=url, content=s,
                            )
                            page.sites.add(settings.SITE_ID)
                        except UnicodeDecodeError:
                            self.stdout.write(
                                'Flatfile creation - skipping undecodable file:'
                                ' %s%s' % (filename, os.linesep)
                            )



