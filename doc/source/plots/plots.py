import matplotlib
matplotlib.use('QT5Agg')
from matplotlib import pyplot

from hubflow.core import *
import pyqtgraph as pg
import pyqtgraph.exporters

import enmapboxtestdata

def exportPyQtGraphPNG(pw, filename):
    exporter = pg.exporters.ImageExporter(pw.plotItem)
    #exporter.parameters()['width'] = 100
    #exporter.parameters()['height'] = 75
    exporter.export(filename)

def exportMatplotlibPNG(filename):
    pyplot.savefig(filename, bbox_inches='tight')

def wavebandDefinition_plot():
    pw = SensorDefinition.fromPredefined(name='sentinel2').wavebandDefinition(index=2).plot()
    exportPyQtGraphPNG(pw, filename='wavebandDefinition_plot.png')

def sensorDefinition_plot():
    pw = SensorDefinition.fromPredefined(name='sentinel2').plot()
    exportPyQtGraphPNG(pw, filename='sensorDefinition_plot.png')

def sensorDefinition_resampleRaster():
    sentinel2Sensor = SensorDefinition.fromPredefined(name='sentinel2')
    enmapRaster = Raster(filename=enmapboxtestdata.enmap)
    resampled = sentinel2Sensor.resampleRaster(filename='/vsimem/resampledLinear.bsq', raster=enmapRaster)
    pixel = Pixel(x=0, y=0) # select single pixel
    plotWidget = enmapRaster.plotZProfile(pixel=pixel, spectral=True, xscale=1000) # draw original enmap profile
    resampled.plotZProfile(pixel=pixel, spectral=True, plotWidget=plotWidget) # draw resampled profile on top
    exportPyQtGraphPNG(plotWidget, filename='sensorDefinition_resampleRaster.png')

def sensorDefinition_resampleProfiles():
    sentinel2Sensor = SensorDefinition.fromPredefined(name='sentinel2')
    enmapRaster = Raster(filename=enmapboxtestdata.enmap)
    enmapArray = enmapRaster.array().reshape((enmapRaster.shape()[0], -1)).T
    resampled = sentinel2Sensor.resampleProfiles(array=enmapArray, wavelength=enmapRaster.metadataWavelength(), wavelengthUnits='nanometers')
    index = 0 # select single profile
    plotWidget = pg.plot(x=enmapRaster.metadataWavelength(), y=enmapArray[index]) # draw original enmap profile
    plotWidget.plot(x=[wd.center() for wd in sentinel2Sensor.wavebandDefinitions()], y=resampled[index]) # draw resampled profile on top
    exportPyQtGraphPNG(plotWidget, filename='sensorDefinition_resampleProfiles.png')

def mask_fromVector():
    vector = Vector(filename=enmapboxtestdata.landcover)
    grid = Raster(filename=enmapboxtestdata.enmap).grid()
    mask = Mask.fromVector(filename='/vsimem/mask.bsq', vector=vector, grid=grid)
    mask.plotSinglebandGrey(showPlot=False)
    exportMatplotlibPNG(filename='mask_fromVector.png')

def vector_fromRandomPointsFromMask():
    grid = Raster(filename=enmapboxtestdata.enmap).grid()
    mask = Mask.fromVector(filename='/vsimem/mask.bsq',
                           vector=Vector(filename=enmapboxtestdata.landcover), grid=grid)
    mask.plotSinglebandGrey(showPlot=False)
    exportMatplotlibPNG(filename='mask_fromVector.png')

    points = Vector.fromRandomPointsFromMask(mask=mask, n=10, filename=join(tempfile.gettempdir(), 'vector.shp'))
    Mask.fromVector(filename='/vsimem/mask.bsq', vector=points, grid=grid).plotSinglebandGrey(showPlot=False)
    exportMatplotlibPNG(filename='vector_fromRandomPointsFromMask.png')

def vector_fromRandomPointsFromClassification():
    grid = Raster(filename=enmapboxtestdata.enmap).grid()
    vectorClassification = VectorClassification(filename=enmapboxtestdata.landcover,
                                                classAttribute=enmapboxtestdata.landcoverAttributes.Level_2_ID,
                                                classDefinition=ClassDefinition(colors=enmapboxtestdata.landcoverClassDefinition.level2.lookup),
                                                oversampling=5)
    classification = Classification.fromClassification(filename='/vsimem/classification.bsq', classification=vectorClassification, grid=grid)
    classification.plotCategoryBand(showPlot=False)
    exportMatplotlibPNG(filename='classification_fromClassification.png')

    points = Vector.fromRandomPointsFromClassification(classification=classification, n=[10]*6, filename=join(tempfile.gettempdir(), 'vector.shp'))
    labels = classification.applyMask(filename='/vsimem/labels.bsq', mask=points)
    labels.plotCategoryBand(showPlot=False)
    exportMatplotlibPNG(filename='classification_applyMask.png')

vector_fromRandomPointsFromClassification()
exit(0)
vector_fromRandomPointsFromMask()
wavebandDefinition_plot()
sensorDefinition_plot()
sensorDefinition_resampleRaster()
sensorDefinition_resampleProfiles()
mask_fromVector()