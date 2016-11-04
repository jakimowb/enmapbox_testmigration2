from __future__ import print_function
import os
from collections import OrderedDict

import numpy
from sklearn.kernel_ridge import KernelRidge
#from sklearn.grid_search import GridSearchCV
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error
from sklearn.neighbors import KernelDensity


import matplotlib.pyplot as plt
from rios.pixelgrid import pixelGridFromFile, findCommonRegion, PixelGridDefn

from hub.timing import tic, toc
from enmapbox.processing.workflow.types import (Workflow, Image, ImageBlock, ImageCollection, ImageCollectionBlock,
    ImageCollectionList, ImageCollectionListBlock, assertType, GDALMeta, Date)
from hub.gdal.util import gdal_rasterize
from hub.ogr.util import ogr2ogr
from osgeo import ogr

class Extracting(Workflow):

    def apply(self, info):

        pass

def testExtracting():

    pass
    workflow = Extracting()
    workflow.run()



class Stacking(Workflow):

    def apply(self, info):

        scenes1 = assertType(self.inputs.scenes1, ImageCollectionListBlock)
        scenes2 = assertType(self.inputs.scenes2, ImageCollectionListBlock)

        fmask = list()
        sr = {i:list() for i in range(6)}
        bandNames = list()
        wavelength = list()
        for scenes in [scenes1, scenes2]:
            for id, scene in scenes.collections.items():
                bandNames.append(id)
                wavelength.append(Date.fromLandsatSceneID(id).decimalYear)
                fmask.append(scene.images[id+'_qa'].cube)
                for i in range(6):
                    sr[i].append(scene.images[id+'_sr'].cube[i])

        fmask = numpy.vstack(fmask)
        fmaskMeta = GDALMeta()
        fmaskMeta.setBandNames(bandNames)
        fmaskMeta.setNoDataValue(255)
        fmaskMeta.setMetadataItem('wavelength', wavelength)

        for i in range(6):
            sr[i] = numpy.array(sr[i])
        srMeta = GDALMeta()
        srMeta.setBandNames(bandNames)
        srMeta.setNoDataValue(-9999)
        srMeta.setMetadataItem('wavelength', wavelength)

        self.outputs.fmask = ImageBlock(cube=fmask, meta=fmaskMeta)
        for i, key in enumerate(['blue', 'green', 'red', 'nir', 'swir1', 'swir2']):
            setattr(self.outputs, key, ImageBlock(cube=sr[i], meta=srMeta))

def testStacking():

    # convert complete archive to LandsatX
    '''from lamos.operators.landsat_x import LandsatXComposer
    from lamos.processing.types import WRS2Footprint
    WRS2Footprint.createUtmLookup(infolder=r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test')
    composer = LandsatXComposer(inextension='.img')
    composer.composeWRS2Archive(infolder=r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test', outfolder=r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_LandsatX', processes=20)
    return'''

    workflow = Stacking()
    workflow.infiles.scenes1 = ImageCollectionList(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_LandsatX\221\070')
    workflow.infiles.scenes2 = ImageCollectionList(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_LandsatX\221\071')
    workflow.outfiles.fmask = Image(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_stacks\fmask')
    for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2']:
        setattr(workflow.outfiles, key, Image(os.path.join(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test_stacks_big', key)))

    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()
    #workflow.controls.setWindowXsize(10)
    #workflow.controls.setWindowYsize(10)

    pixelGrid = pixelGridFromFile(r'G:\Rohdaten\Brazil\Raster\LANDSAT\TS_RBF_test\221\071\LC82210712013162LGN00\LC82210712013162LGN00_cfmask.img')

    print
    # very small test region inside the overlapping region of both footprints
    if 0:
        pixelGrid.xMin = 202425
        pixelGrid.yMin = -1680165
        pixelGrid.xMax = pixelGrid.xMin + 30*10
        pixelGrid.yMax = pixelGrid.yMin + 30*10

    # region provided by Marcel
    if 1:
        pixelGrid.xMin = 149655
        pixelGrid.xMax = 254025
        pixelGrid.yMin = -1521285
        pixelGrid.yMax = -1809825

        pixelGrid.yMax = -1521285
        pixelGrid.yMin = -1809825

    workflow.controls.setReferencePixgrid(pixelGrid)
    workflow.controls.setResampleMethod('near')

    workflow.run()


CToAlpha = lambda C: 1. / (2 * C)  # alpha corresponds to (2*C)^-1 in other models such as SVR.
sigmaToGamma = lambda sigma: 1. / (2 * sigma ** 2)
gammaToSigma = lambda gamma: numpy.sqrt(1. / (2 * gamma))

class Fitting(Workflow):

    def apply(self, info):

        def validPoints(key, sample, line):
            valid = validCube[:, line, sample]
            if key is None:
                return x[valid], numpy.array([yi[valid, line, sample] for yi in y.values()]).T
            else:
                return x[valid], y[key][valid, line, sample]

        def validPointsScreened(key, sample, line, model):

            # !!! skip screeneing !!!
            xy = validPoints(key, sample, line)
            return xy

            # screening
            x2, y2 = validPoints('green', sample, line)
            y2_pred = p_(x2, x2, y2, model, sample_weight=1-kde.X_fit_density_)

            x5, y5 = validPoints('swir1', sample, line)
            y5_pred = p_(x5, x5, y5, model, sample_weight=1-kde.X_fit_density_)

            valid = numpy.logical_not((y2-y2_pred > 0.04*10000) + (y5-y5_pred < -0.04*10000))

            xy = validPoints(key, sample, line)
            return xy[0][valid], xy[1][valid]

        def p(key, x, sample, line, model, sample_weight):
            x_train, y_train = validPointsScreened(key, sample, line, model)

            '''if refit:
                y_pred_train = p_(x_train, x_train, y_train, model, sample_weight=None)
                errors =  abs(y_pred_train-y_train)
                max = 500
                sample_weight = numpy.clip(max-errors, 0, max)/max
                sample_weight = numpy.mean(sample_weight, axis=1)
                print
            else:
                sample_weight = None'''

            y_pred = p_(x, x_train, y_train, model, sample_weight=sample_weight)
            y_error = residuals(x, x_train, y_train, y_train_pred=p_(x_train,x_train, y_train, model, sample_weight=sample_weight))
            return y_pred, y_error


        def residuals(x, x_train, y_train, y_train_pred):
            y_error = abs(y_train-y_train_pred)
            y_error_pred = krrError.fit(x_train, y_error).predict(x)
            return y_error_pred

        def p_(x, x_train, y_train, model, sample_weight):
            model.fit(x_train, y_train, sample_weight=sample_weight)
            y_pred = model.predict(x)#, return_std=False)
            return y_pred

        def bestPixelCompositing(i, x, sample, line):
            x_valid, y_valid = validPointsScreened(i, sample, line)
            x_pred = list()
            y_pred = list()
            for i, xi in enumerate(x[:,0]):
                index = numpy.argmin(abs(x_valid-xi))
                if abs(x_valid[index]-xi) < 5./365.:
                    x_pred.append(xi)
                    y_pred.append(y_valid[index])
            return x_pred, y_pred

        # obvervation dates [decimal years]
        x = numpy.array(self.inputs.fmask.meta.getMetadataItem('wavelength'), dtype=numpy.float64)[:, numpy.newaxis]

        # prepare data cubes
        validCube = self.inputs.fmask.cube <= 1
        y = OrderedDict()
        colors = OrderedDict() # http://matplotlib.org/examples/color/named_colors.html
        for key, color in zip(['blue', 'green', 'red', 'nir', 'swir1', 'swir2'], ['b', 'g', 'r', 'm', 'cyan', 'lightskyblue']):
            y[key] = getattr(self.inputs, key).cube
            colors[key] = color
        #y['ndvi'] = numpy.true_divide(y['nir']-y['red'], y['nir']+y['red']) *10000
        #colors['ndvi'] = 'darkgreen'

        # grid for plotting
        x_grid = numpy.linspace(x.min(), x.max(), (x.max()-x.min())*365., dtype=numpy.float64)[:, numpy.newaxis]

        # create KernelRidgeRegressor
        #param_grid = {'gamma': [sigmaToGamma(days / 365.) for days in [5, 10, 15, 20, 30, 60, 90, 120, 150, 180]]}
        param_grid = {'gamma': [sigmaToGamma(days / 365.) for days in [150]]}

#        param_grid = {'gamma': [sigmaToGamma(0.5)]}

        C = 1e4

        #scoring = 'neg_mean_absolute_error'
        #krrTuned = GridSearchCV(KernelRidge(alpha=CToAlpha(C), kernel='rbf'), cv=10, param_grid=param_grid, scoring=scoring)
        from sklearn.gaussian_process.kernels import ConstantKernel, RBF, ExpSineSquared
        kernel = RBF(30*4/365.) + RBF(30*6/365.) # + ExpSineSquared(length_scale=20, periodicity=1) + ExpSineSquared(periodicity=0.5, length_scale=20)
        krrFixed = KernelRidge(kernel=kernel, alpha=CToAlpha(C))
        krrError = KernelRidge(kernel='rbf', gamma=sigmaToGamma(10), alpha=CToAlpha(C))

        kde = KernelDensity(kernel='gaussian', bandwidth=60./365)

        # fit and plot
        lines, samples = validCube.shape[1:]
        for line in range(lines):
            for sample in range(samples):

                ### 3d plot ###
                if 1:
                    X = list()
                    Z = list()
                    sample_weight = None  # 1. - kde.X_fit_density_
                    y_multi_pred_grid, y_multi_error_grid = p(None, x_grid, sample, line, krrFixed,
                                                              sample_weight=sample_weight)

                    for i, (name, cube) in enumerate(y.items()):

                        y_pred_grid = y_multi_pred_grid[i]
                        X.append(x_grid)                                                    # time
                        Z.append(y_pred_grid)                                               # sr

                        #######
                    Y = numpy.array([480.0, 560.0, 655.0, 865.0, 1585.0, 2200.0])  # wavelength
                    plot3d(X, Y, Z)

                # fit density
                kde.fit(x[validCube[:, line, sample]])
                kde.X_fit_ = x[validCube[:, line, sample]]
                kde.X_fit_density_ = numpy.exp(kde.score_samples(kde.X_fit_))

                ### train multi-label KRR ###
                sample_weight = None #1. - kde.X_fit_density_
                y_multi_pred_grid, y_multi_error_grid = p(None, x_grid, sample, line, krrFixed, sample_weight=sample_weight)
                #y_multiRefit_pred_grid, y_multiRefit_error_grid = p(None, x_grid, sample, line, krrFixed, refit=True)

                for i, (name, cube) in enumerate(y.items()):
                    #if name != 'ndvi': continue

                    #plt.figure(figsize=(15,10))



                    #todo: use residuals as weights :-)
                    #fit multi-target KRR

                    # tuned model
                    #y_pred_grid, y_error_grid = p(name, x_grid, sample, line, krrTuned)
                    #plt.plot(x_grid, y_pred_grid, linestyle='-', color=colors[name], label=name+' (tuned)')#+' Sigma='+str(int(gammaToSigma(krr.best_params_['gamma'])*365))+' days')

                    # fixed model
                    #y_pred_grid, y_error_grid = p(name, x_grid, sample, line, krrFixed)
                    #plt.plot(x_grid, y_pred_grid, linestyle='-', color=colors[name], label=name+' (fixed)')#+' Sigma='+str(int(gammaToSigma(krr.best_params_['gamma'])*365))+' days')
                    #plt.fill_between(x_grid[:, 0], y_pred_grid - y_error_grid, y_pred_grid + y_error_grid,
                    #                 alpha=0.15, color=colors[name])

                    # multi target model
                    y_pred_grid, y_error_grid = y_multi_pred_grid[:, i], y_multi_error_grid[:, i]
                    plt.plot(x_grid, y_pred_grid, linestyle='-', color=colors[name])#, label=name + ' (multi s=' + str(int(kernel.length_scale*365)) + 'days)')

                    # multiRefit target model
                    #y_pred_grid, y_error_grid = y_multiRefit_pred_grid[:, i], y_multiRefit_error_grid[:, i]
                    #plt.plot(x_grid, y_pred_grid, linestyle='--', color=colors[name], label=name + ' (multiRefit)')

                    #plt.scatter(x, y[name][:, line, sample], c='r', edgecolors='r')

                    #x_valid, y_valid = validPoints(name, sample, line)
                    x_valid_screened, y_valid_screened = validPointsScreened(name, sample, line, krrFixed)
                    #plt.scatter(x_valid, y_valid, c='y', edgecolors='y')
                    plt.scatter(x_valid_screened, y_valid_screened, c=colors[name], edgecolors='None')

                    # plot density
                    #plt.plot(x_grid, numpy.exp(kde.score_samples(x_grid)) * 10000, linestyle='-', color='grey')
                    plt.plot(x_grid, numpy.exp(kde.score_samples(x_grid)) * 10000, linestyle=':', color='grey')

                    plt.xlim(x_grid.min(), x_grid.max())
                    plt.ylim(0,12000)
                    plt.xlabel('Year')
                    plt.ylabel('surface reflectance x 10k')
                    plt.title(self.inargs.point['class']+ ' (Point ' +str(self.inargs.point['i']+1) +')\nMapXY = ('+str(self.inargs.point['x'])+', '+str(self.inargs.point['y'])+')'+ '\nsigma = ' + str(kernel)) #str(int(kernel.length_scale*365)) + ' days')
                    #plt.tight_layout()
                    #plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=3, shadow=True, title="Legend", fancybox=True)

                if self.inargs.showPDF:
                    self.inargs.pdf.savefig()
                    plt.close()
                else:
                    plt.show()


                    #return

        #self.outputs.imageCollectionList = imageCollectionListCopy

def plot3d(X,Y,Z):
    from mpl_toolkits.mplot3d import axes3d
    import matplotlib.pyplot as plt


    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    X = numpy.array(X)[:,:,0]
    Y = Y[:,None]*numpy.ones_like(X)
    Z = numpy.array(Z)
    ax.plot_wireframe(X, Y, Z, rstride=1, cstride=5)

    plt.show()

def getPoints():

    outfile = r'C:\Work\data\marcel\reference\sample_profiles_intersection.shp'
    driver = ogr.GetDriverByName("ESRI Shapefile")
    dataSource = driver.Open(outfile, 0)
    layer = dataSource.GetLayer()
    points = list()
    for i, feature in enumerate(layer):
        point = OrderedDict()
        point['i'] = i
        point['x'] = feature.GetGeometryRef().GetX()
        point['y'] = feature.GetGeometryRef().GetY()
        point['class'] = feature.GetField('Class')
        points.append(point)
    return points

def testFitting():


    points = getPoints()

    from matplotlib.backends.backend_pdf import PdfPages
    with PdfPages(r'C:\Work\data\marcel\plots.pdf') as pdf:
        for point in points:

            pixelGrid = pixelGridFromFile(r'C:\Work\data\marcel\TS_RBF_test_stacks_big_intersection\fmask.tif')
            pixelGrid.xMin = point['x']
            pixelGrid.yMin = point['y']
            pixelGrid.xMax = point['x']+30
            pixelGrid.yMax = point['y']+30


            workflow = Fitting()
            workflow.inargs.showPDF = 0
            workflow.inargs.pdf = pdf
            workflow.inargs.point = point


            for key in ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'fmask']:
                setattr(workflow.infiles, key, Image(os.path.join(r'C:\Work\data\marcel\TS_RBF_test_stacks_big_intersection', key+'.tif')))
            print(pixelGrid)

            workflow.controls.setReferencePixgrid(pixelGrid)
            workflow.controls.setResampleMethod('near')

            workflow.run()
            #return

if __name__ == '__main__':

    tic()
    testFitting()
    toc()
