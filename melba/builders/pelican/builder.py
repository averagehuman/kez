
import os
import sys
import copy

from pelican import Pelican
from pelican.settings import DEFAULT_CONFIG, DEFAULT_THEME, PYGMENTS_RST_OPTIONS
from pelican.settings import configure_settings

pathjoin = os.path.join
pathexists = os.path.exists
dirname = os.path.dirname
basename = os.path.basename
isabs = os.path.isabs

PLUGIN_PATH = pathjoin(dirname(__file__), 'plugins')
MELBA_THEMES = pathjoin(dirname(__file__), 'themes')

def build(src, dst, options, local_settings, stdout=sys.stdout, stderr=sys.stderr):
    """The main Pelican build function"""
    theme_path = options.get('theme_path', MELBA_THEMES)
    settings = get_settings(src, dst, theme_path, local_settings)
    pelican = Pelican(settings)
    pelican.run()

def get_settings(src, dst, theme_path, overrides):
    """Generate Pelican settings dict and normalize certain options"""
    settings = copy.deepcopy(DEFAULT_CONFIG)
    settings.update(overrides)
    settings['PATH'] = norm_content_path(src, settings['PATH'])
    settings['OUTPUT_PATH'] = dst
    settings['PLUGIN_PATH'] = PLUGIN_PATH
    settings['DELETE_OUTPUT_DIRECTORY'] = False
    theme = settings.get('THEME', '').strip('/')
    if theme:
        theme = pathjoin(src, theme)
        if not pathexists(theme):
            theme = pathjoin(theme_path, theme)
            if not pathexists(theme):
                theme = None
    settings['THEME'] = theme or DEFAULT_THEME
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



