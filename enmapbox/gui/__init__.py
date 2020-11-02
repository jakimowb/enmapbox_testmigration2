
# import QPS modules
from ..externals.qps.crosshair.crosshair import CrosshairStyle, CrosshairWidget, CrosshairMapCanvasItem, CrosshairDialog, getCrosshairStyle
from ..externals.qps.plotstyling.plotstyling import PlotStyle, PlotStyleDialog, PlotStyleButton, PlotStyleWidget
from ..externals.qps.speclib.core import SpectralLibrary, SpectralProfile
from ..externals.qps.speclib.gui import SpectralLibraryWidget, AbstractSpectralLibraryIO
from ..externals.qps.classification.classificationscheme import ClassificationScheme, ClassInfo, ClassificationSchemeComboBox, ClassificationSchemeWidget, ClassificationSchemeDialog, hasClassification
from ..externals.qps.models import Option, OptionListModel, TreeNode, TreeModel, TreeView, PyObjectTreeNode
from ..externals.qps.simplewidgets import SliderSpinBox, DoubleSliderSpinBox
from ..externals.qps.maptools import *
from ..externals.qps.layerproperties import subLayerDefinitions, subLayers, \
    openRasterLayerSilent, defaultBands, defaultRasterRenderer, showLayerPropertiesDialog
from ..externals.qps.resources import ResourceBrowser, scanResources
