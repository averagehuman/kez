
import os
import sys
import copy

from pelican import Pelican
from pelican.settings import DEFAULT_CONFIG, DEFAULT_THEME, PYGMENTS_RST_OPTIONS
from pelican.settings import configure_settings

from kez.utils import urlparse
from kez.models import Project

pathjoin = os.path.join
pathexists = os.path.exists
dirname = os.path.dirname
basename = os.path.basename
abspath = os.path.abspath
isabs = os.path.isabs

KEZ_PLUGIN_PATH = pathjoin(abspath(dirname(__file__)), 'plugins')
KEZ_PLUGINS = [
    'html_rst_directive',
    #'ipython',
    'multi_part',
    'neighbors',
]
KEZ_THEMES = pathjoin(abspath(dirname(__file__)), 'themes')

def build(src, dst, vcs_cache, options, local_settings, stdout=sys.stdout, stderr=sys.stderr):
    """The main Pelican build function"""
    theme_path = options.get('theme_path', KEZ_THEMES)
    theme = local_settings.get('THEME', '').strip('/')
    theme_url = local_settings.get('THEME_URL', '').strip('/')
    pathto = None
    # checkout remote theme
    if theme_url:
        _, repo = Project.from_url(theme_url, vcs_cache)
        repo.checkout()
        pathto = repo._checkout
    if theme:
        # check subpath existence (relative to remote theme root or document source root)
        pathto = pathjoin(pathto or src, theme)
        if not pathexists(pathto):
            pathto = pathjoin(theme_path, theme)
            if not pathexists(pathto):
                pathto = None
    local_settings['THEME'] = pathto or theme or DEFAULT_THEME
    settings = get_settings(src, dst, theme_path, local_settings)
    pelican = Pelican(settings)
    pelican.run()

def get_settings(src, dst, theme_path, local_settings):
    """Generate Pelican settings dict and normalize certain options"""
    settings = copy.deepcopy(DEFAULT_CONFIG)
    settings.update(local_settings)
    settings['PATH'] = norm_content_path(src, settings['PATH'])
    settings['OUTPUT_PATH'] = dst
    settings['PLUGIN_PATH'] = KEZ_PLUGIN_PATH
    settings['PLUGINS'] = KEZ_PLUGINS
    settings['DELETE_OUTPUT_DIRECTORY'] = False
    global PYGMENTS_RST_OPTIONS
    PYGMENTS_RST_OPTIONS = settings.get('PYGMENTS_RST_OPTIONS', None)
    settings['PELICAN_CLASS'] = 'pelican.Pelican'
    #updated = {}
    #for key, val in settings.items():
    #    if key in STATIC_PATH_SETTINGS:
    #        updated[key] = norm_path_setting(src, val)
    #settings.update(updated)
    return configure_settings(settings)

def norm_content_path(root, path):
    """Ensure the PATH setting is a subdirectory of the repository root"""
    if not path:
        src = None
    if isabs(path):
        if path.startswith(root):
            src = path
        else:
            src = None
    else:
        src = pathjoin(root, path)
    if src and pathexists(src):
        return src
    else:
        # PATH was not set or badly set, fallback to returning the repository root
        return root



