from bokeh.plotting import figure
from bokeh.io import output_notebook, show
import numpy as np
from hubdc.model import Raster

def displayMultibandColor(image, indices=None, ranges=None, title=''):

    if indices is None:
        indices = (0, 1, 2)

    if ranges is None:
        ranges = (0, 255)

    if len(ranges) == 2:
        ranges = (ranges, ) * 3

    if isinstance(image, np.ndarray):
        assert image.ndim == 3
        image = [image[index] for index in indices]
        ysize, xsize = image[0].shape
        x_range = [0, xsize]
        y_range = [ysize, 0]
    elif isinstance(image, Raster):
        image = [image.band(index=index).readAsArray() for index in indices]
        ysize, xsize = image[0].shape
        x_range = [0, xsize]
        y_range = [ysize, 0]

    for band in image:
        assert isinstance(band, np.ndarray)
        assert band.ndim == 2

    rgba = imageToRGBA(image=image, ranges=ranges)

    p = figure(title=title, plot_width=min(xsize, 500), plot_height=min(ysize, 500), x_range=[0, xsize], y_range=[ysize, 0])
    p.image_rgba(image=[rgba], x=[0], y=[ysize], dw=[xsize], dh=[ysize])
    show(p)


def displaySinglebandGrey(band, index=0, range=None, title=''):
    if isinstance(band, np.ndarray):
        if band.ndim == 3:
            band = band[index]
        assert band.ndim == 2
        displayMultibandColor(image=[band] * 3, ranges=range, title=title)
    elif isinstance(band, Raster):
        displayMultibandColor(image=band, indices=[index] * 3, ranges=range, title=title)


def displaySinglebandPseudocolor(band, index=0, range=None, colormap='RdYlGn', title=''):

    if range is None:
        range = (0, 255)

    if isinstance(band, np.ndarray):
        if band.ndim == 3:
            band = band[index]
        assert band.ndim == 2
    elif isinstance(band, Raster):
        band = band.band(index=index).readAsArray()

    grey = bandToGrey(band, range=range)
    ysize, xsize = band.shape
    p = figure(title=title, plot_width=xsize, plot_height=ysize, x_range=[0, xsize], y_range=[ysize, 0])
    p.image(image=[grey], x=[0], y=[ysize], dw=[xsize], dh=[ysize], palette=get_cmap(name=colormap))
    show(p)


def imageToRGBA(image, ranges):
    rgba = list()
    for band, (min, max) in zip(image, ranges):
        grey = np.float32(band)
        if callable(min):
            min = min(grey)
        if callable(max):
            max = max(grey)
        grey -= min
        grey /= max - min
        grey *= 255
        np.clip(grey, 0, 255, out=grey)
        rgba.append(grey)
    rgba.append(np.full_like(image[0], fill_value=255, dtype=np.uint8))  # no transparency
    rgba = np.array(rgba, dtype=np.uint8)
    rgba = np.transpose(rgba, [1, 2, 0])
    rgba = rgba[::-1]
    return rgba


def bandToGrey(band, range):
    grey = np.float32(band)
    min, max = range
    grey -= min
    grey /= max - min
    grey *= 255
    np.clip(grey, 0, 255, out=grey)
    grey = np.uint8(grey)
    grey = grey[::-1]
    return grey


def get_cmap(name=None, lut=None):
    '''Create a Bokeh palette from a Matplotlib color map.'''
    import matplotlib as plt
    import matplotlib.cm as cm
    colormap = cm.get_cmap(name=name, lut=lut)
    bokehpalette = [plt.colors.rgb2hex(m) for m in colormap(np.arange(colormap.N))]
    return bokehpalette

from hubdc.testdata import *
from hubdc.model import *
r = openRaster(LT51940232010189KIS01.nir)
v = openVector(BrandenburgDistricts.shp)
#band = r.readAsArray()
#displaySinglebandGrey(band=band, dataStretch=(np.min, np.max), title='Landsat NIR')
displaySinglebandGrey(band=r, range=(0, 50), title='Landsat NIR')
displaySinglebandPseudocolor(band=r, range=(0, 50), colormap='RdYlGn', title='Landsat NIR')
#grid=Grid(extent=v.spatialExtent(), resolution=Resolution(x=0.005, y=0.005))
#r = v.rasterize(grid=grid)
#band = r.readAsArray()
#displaySinglebandGrey(band=band, dataStretch=(0, 1), title='Brandenburg')