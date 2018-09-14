# -*- coding: utf-8 -*-
#
# EnMAP-Box 3 documentation build configuration file, created by
# sphinx-quickstart on Fri Jan 19 05:59:30 2018.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os, re, datetime
import sys
import mock
import numpy as np
from PyQt5 import uic, QtCore, QtGui, QtWidgets, QtXml
import PyQt5

#sys.modules['qgis.PyQt'] = PyQt5
#for m in [uic, QtCore, QtGui, QtWidgets, QtXml]:
#    sys.modules['qgis.PyQt.{}'.format(m.__name__.split('.')[-1])] = m

if True:
    MOCK_MODULES = ['qgis','qgis.core','qgis.gui','qgis.utils',
                'vrtbuilder','vrtbuilder.virtualrasters',
                'qgis.PyQt','qgis.PyQt.Qt','qgis.PyQt.QtCore','qgis.PyQt.QtGui','qgis.PyQt.QtWidgets','qgis.PyQt.QtXml',
                'processing','processing.core','processing.core.ProcessingConfig']

    for mod_name in MOCK_MODULES:
        sys.modules[mod_name] = mock.Mock()

if False:
    pathMockedNames = os.path.join(os.path.dirname(__file__),'mockednameslist.txt')
    print('Read mocked names list')
    f = open(pathMockedNames, 'r', encoding='utf-8')
    lines = f.read().splitlines()
    f.close()
    for l in lines:

        sys.modules[l] = mock.NonCallableMagicMock()


autodoc_mock_imports = ['vrtbuilder',
                'gdal','sklearn','numpy', 'scipy', 'matplotlib', 'matplotlib.pyplot', 'scipy.interpolate',
                'qgis','qgis.utils','qgis.core','qgis.gui',
                'processing', 'processing.core.ProcessingConfig'
]
autodoc_warningiserror = False

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../../'))

import os, sys, re
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtSvg import *

def convert2png(pathSVG:str):
    if os.path.isfile(pathSVG) and pathSVG.endswith('.svg'):
        pathPNG = re.sub('\.svg$','.png', pathSVG)
        image = QImage(pathSVG)
        image.save(pathPNG)


# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc',
    #'sphinxcontrib.mockautodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    #'sphinx.ext.autosectionlabel',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_parsers = {
   '.md': 'recommonmark.parser.CommonMarkParser',
}

source_suffix = ['.rst', '.md']
#source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'EnMAP-Box 3'
copyright = u'2018, Andreas Rabe, Benjamin Jakimow, Sebastian van der Linden, Patrick Hostert'
author = u'Fabian Thiel,\nAndreas Rabe,\nBenjamin Jakimow,\nSebastian van der Linden,\nPatrick Hostert'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#

import enmapbox
timestamp = ''.join(np.datetime64(datetime.datetime.now()).astype(str).split(':')[0:-1]).replace('-','')
buildID = '{}.{}'.format(re.search(r'(\.?[^.]*){2}', enmapbox.__version__).group(), timestamp)


# The short X.Y version.
version = u'{}'.format(re.search(r'(\.?[^.]*){2}', enmapbox.__version__).group())
# The full version, including alpha/beta/rc tags.
release = u'{}'.format(buildID)

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = []

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
#html_theme = 'alabaster'
#html_theme = 'classic'
html_theme = 'sphinx_rtd_theme'
# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
html_theme_options = {
    'canonical_url': '',
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': 'view',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

html_logo = 'img/enmap_logo_black.png'
html_favicon = 'img/enmap_logo_black.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
#
# This is required for the alabaster theme
# refs: http://alabaster.readthedocs.io/en/latest/installation.html#sidebars
html_sidebars = {
    '**': [
        'about.html',
        'navigation.html',
        'relations.html',  # needs 'show_related': True theme option to display
        'searchbox.html',
        'donate.html',
    ]
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'EnMAPBoxDoc'


# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #
    # 'papersize': 'letterpaper',

    # The font size ('10pt', '11pt' or '12pt').
    #
    # 'pointsize': '10pt',

    # Additional stuff for the LaTeX preamble.
    #
    # 'preamble': '',

    # Latex figure (float) alignment
    #
    # 'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'EnMAP-Box3.tex', u'EnMAP-Box 3 Documentation',
     u'Andreas Rabe, Benjamin Jakimow, Sebastian van der Linden, Patrick Hostert', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    (master_doc, 'enmap-box3', u'EnMAP-Box 3 Documentation',
     [author], 1)
]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'EnMAP-Box3', u'EnMAP-Box 3 Documentation',
     author, 'EnMAP-Box3', 'One line description of project.',
     'Miscellaneous'),
]




# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'https://docs.python.org/': None}

# adding this because in pycookbook a lot of text is referencing classes, which cannot be found by sphinx
# eg: Map canvas is implemented as :class:`QgsMapCanvas` ...
# I hope somebody will create the real references for these so they can be removed here...
nitpicky = True
nitpick_ignore = [('py:class', 'QAction'),
                  ('py:class', 'QDomElement'),
                  ('py:class', 'QFileInfo'),

                  ('py:class', 'QSettings'),

                  ('py:class', 'QGraphicsScene'),
                  ('py:class', 'QgsAccessControlFilter'),
                  ('py:class', 'QgsCategorizedSymbolRendererV2'),
                  ('py:class', 'QgsComposerItem'),
                  ('py:class', 'QgsComposition'),
                  ('py:class', 'QgsCoordinateReferenceSystem'),
                  ('py:class', 'QgsCoordinateTransform'),
                  ('py:class', 'QgsDataSourceUri'),
                  ('py:class', 'QgsDistanceArea'),
                  ('py:class', 'QgsEditError'),
                  ('py:class', 'QgsExpression'),
                  ('py:class', 'QgsFeature'),
                  ('py:class', 'QgsFeatureRendererV2'),
                  ('py:class', 'QgsFields'),
                  ('py:class', 'QgsFillSymbolV2'),
                  ('py:class', 'QgsGeometry'),
                  ('py:class', 'QgsGraduatedSymbolRendererV2'),
                  ('py:class', 'QgsGraphAnalyzer'),
                  ('py:class', 'QgsInterface'),
                  ('py:class', 'QgisInterface'),
                  ('py:class', 'QgsLayerTreeMapCanvasBridge'),
                  ('py:class', 'QgsLineSymbolV2'),
                  ('py:class', 'QgsLogger'),
                  ('py:class', 'QgsMapCanvas'),
                  ('py:class', 'QgsMapCanvasItem'),
                  ('py:class', 'QgsMapCanvasItem'),
                  ('py:class', 'QgsMapCanvasMap'),
                  ('py:class', 'QgsMapRenderer'),
                  ('py:class', 'QgsMapRendererJob'),
                  ('py:class', 'QgsMapServiceException'),
                  ('py:class', 'QgsMapTool'),
                  ('py:class', 'QgsMapToolPan'),
                  ('py:class', 'QgsMapToolZoom'),
                  ('py:class', 'QgsMarkerSymbolV2'),
                  ('py:class', 'QgsMessageBar'),
                  ('py:class', 'QgsMessageLog'),
                  ('py:class', 'QgsPoint'),
                  ('py:class', 'QgsPointXY'),
                  ('py:class', 'QgsPluginManagerInterface'),
                  ('py:class', 'QgsProject'),
                  ('py:class', 'QgsRasterLayer'),
                  ('py:class', 'QgsRasterDataProvider'),
                  ('py:class', 'QgsRasterIdentifyResult'),
                  ('py:class', 'QgsRasterRenderer'),
                  ('py:class', 'QgsRendererV2AbstractMetadata'),
                  ('py:class', 'QgsRendererV2Registry'),
                  ('py:class', 'QgsRendererV2Widget'),
                  ('py:class', 'QgsRequestHandler'),
                  ('py:class', 'QgsRubberBand'),
                  ('py:class', 'QgsServerFilter'),
                  ('py:class', 'QgsServerInterface'),
                  ('py:class', 'QgsSingleSymbolRendererV2'),
                  ('py:class', 'QgsStyleV2'),
                  ('py:class', 'QgsSymbolLayerV2'),
                  ('py:class', 'QgsSymbolLayerV2Registry'),
                  ('py:class', 'QgsSymbolV2'),
                  ('py:class', 'QgsVectorColorRampV2'),
                  ('py:class', 'QgsVectorFileWriter'),
                  ('py:class', 'QgsVectorLayer'),
                  ('py:class', 'QgsVectorLayerEditUtils'),
                  ('py:class', 'QgsVertexMarker'),
                  ('py:class', 'QMenu'),
                  ('py:class', 'QSettings'),

                  ('py:data', 'iface'),
                  ('py:data', 'qgis.utils.iface'),

                  ('py:func', 'addFeatures'),
                  ('py:func', 'addPluginToDatabaseMenu'),
                  ('py:func', 'addPluginToMenu'),
                  ('py:func', 'addPluginToRasterMenu'),
                  ('py:func', 'addPluginToVectorMenu'),
                  ('py:func', 'addPluginToWebMenu'),
                  ('py:func', 'angle'),
                  ('py:func', 'asMultiPoint'),
                  ('py:func', 'asMultiPolygon'),
                  ('py:func', 'asMultiPolyline'),
                  ('py:func', 'beginEditCommand'),
                  ('py:func', 'capabilities'),
                  ('py:func', 'capabilitiesString'),
                  ('py:func', 'changed'),
                  ('py:func', 'classAttribute'),
                  ('py:func', 'classFactory'),
                  ('py:func', 'clone'),
                  ('py:func', 'color'),
                  ('py:func', 'commitChanges'),
                  ('py:func', 'contains'),
                  ('py:func', 'create*'),
                  ('py:func', 'createRenderer'),
                  ('py:func', 'createRendererWidget'),
                  ('py:func', 'createSimple'),
                  ('py:func', 'createSpatialIndex'),
                  ('py:func', 'createSymbolLayer'),
                  ('py:func', 'createSymbolLayerWidget'),
                  ('py:func', 'destroyEditCommand'),
                  ('py:func', 'difference'),
                  ('py:func', 'dijkstra'),
                  ('py:func', 'dump'),
                  ('py:func', 'endEditCommand'),
                  ('py:func', 'executeRequest'),
                  ('py:func', 'exitQgis'),
                  ('py:func', 'features'),
                  ('py:func', 'fields'),
                  ('py:func', 'getFeatures'),
                  ('py:func', 'hide'),
                  ('py:func', '__init__'),
                  ('py:func', 'identify'),
                  ('py:func', 'initAttributes'),
                  ('py:func', 'initGui'),
                  ('py:func', 'initGui()'),
                  ('py:func', 'initQgis'),
                  ('py:func', 'instance'),
                  ('py:func', 'intersects'),
                  ('py:func', 'isEditable'),
                  ('py:func', 'isMultipart'),
                  ('py:func', 'isValid'),
                  ('py:func', 'label'),
                  ('py:func', 'layerType'),
                  ('py:func', 'mode'),
                  ('py:func', 'nextFeature'),
                  ('py:func', 'pendingFields'),
                  ('py:func', 'properties'),
                  ('py:func', 'QgsApplication.setPrefixPath'),
                  ('py:func', 'QgsCoordinateReferenceSystem.createFromString'),
                  ('py:func', 'QgsExpression.prepare'),
                  ('py:func', 'read()'),
                  ('py:func', 'read'),
                  ('py:func', 'registerFilter'),
                  ('py:func', 'renderer'),
                  ('py:func', 'renderPoint'),
                  ('py:func', 'renderPolygon'),
                  ('py:func', 'renderPolyline'),
                  ('py:func', 'requestReady'),
                  ('py:func', 'requestReady()'),
                  ('py:func', 'responseComplete'),
                  ('py:func', 'rollBack'),
                  ('py:func', 'sample'),
                  ('py:func', 'selectedFeatures'),
                  ('py:func', 'sendResponse'),
                  ('py:func', 'sendResponse()'),
                  ('py:func', 'serverClassFactory'),
                  ('py:func', 'setClassAttribute'),
                  ('py:func', 'setColor'),
                  ('py:func', 'setDataSource'),
                  ('py:func', 'setIcon'),
                  ('py:func', 'setLimit'),
                  ('py:func', 'setMapTool'),
                  ('py:func', 'setRenderer'),
                  ('py:func', 'select'),
                  ('py:func', 'setSelectionColor'),
                  ('py:func', 'setSymbol'),
                  ('py:func', 'setSymbolLayer'),
                  ('py:func', 'shortestTree'),
                  ('py:func', 'show'),
                  ('py:func', 'size'),
                  ('py:func', 'showPluginHelp'),
                  ('py:func', 'sourceColorRamp'),
                  ('py:func', 'sourceSymbol'),
                  ('py:func', 'startEditing'),
                  ('py:func', 'startRender'),
                  ('py:func', 'stopRender'),
                  ('py:func', 'symbol'),
                  ('py:func', 'symbolForFeature'),
                  ('py:func', 'symbolLayer'),
                  ('py:func', 'transform'),
                  ('py:func', 'type'),
                  ('py:func', 'union'),
                  ('py:func', 'unload'),
                  ('py:func', 'unload()'),
                  ('py:func', 'usedAttributes'),
                  ('py:func', 'value'),
                  ('py:func', 'value()'),
                  ('py:func', 'width'),
                  ('py:func', 'wkbType'),
                  ('py:func', 'write'),
                  ('py:func', 'writeEntry'),
                  ('py:func', 'x'),
                  ('py:func', 'y'),

                  ('py:obj', 'QgsFeatureRequest'),
                  ('py:obj', 'QgsExpression'),

                  ('py:const', 'EpsgCrsId'),
                  ('py:const', 'InternalCrsId'),
                  ('py:const', 'PostgisCrsId'),
                  ('py:const', 'True'),

                  ('py:mod', 'qgis'),
                  ('py:mod', 'numpy'),
                  ('py:mod', 'processing'),
                  ('py:mod', 'pyqtgraph'),
                  ]