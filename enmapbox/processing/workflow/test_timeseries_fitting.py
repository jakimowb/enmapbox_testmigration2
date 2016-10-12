from __future__ import print_function
import os
import numpy
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, RationalQuadratic, ExpSineSquared, ConstantKernel
from sklearn.kernel_ridge import KernelRidge
from sklearn.model_selection import GridSearchCV

from hub.timing import tic, toc
from enmapbox.processing.workflow.types import (Workflow, Image, ImageBlock, ImageCollection, ImageCollectionBlock,
    ImageCollectionList, ImageCollectionListBlock, assertType, GDALMeta, Date)
import matplotlib.pyplot as plt


class TSFitting(Workflow):

    def apply(self, info):
        mgrs = assertType(self.inputs.mgrs, ImageCollectionListBlock)
        timeseries = ImageCollectionBlock(name='timeseries')

        bandNames = ['blue', 'green', 'red', 'nir', 'swir1', 'swir2', 'ndvi']
        dyear = numpy.array([landsat.images[id + '_sr'].meta.getAcquisitionDate().decimalYear for id, landsat in mgrs.collections.items()])
        dyear = dyear.reshape((-1,1)).astype(numpy.float64)
        xstart, xend = 2014, 2016
        x_grid = numpy.linspace(xstart, xend, (xend-xstart)*365., dtype=numpy.float64).reshape((-1,1))
        #x_grid = numpy.linspace(dyear.min(), dyear.max(), (dyear.max()-dyear.min())*365./10.)[:, numpy.newaxis]
        #T_ = numpy.linspace(2014, 2016.5, 1000)[:, numpy.newaxis]

        #C = 1000.
        sigma = 6/12. # in decimal years
        alpha = lambda C: 1./(2*C) # alpha corresponds to (2*C)^-1 in other models such as SVR.
        sigmaToGamma = lambda sigma: 1./(2*sigma**2)
        gammaToSigma = lambda gamma: numpy.sqrt(1./(2*gamma))

        gps = list()
        C = ConstantKernel(1e4, 'fixed')
        #C = ConstantKernel(1e4, (1,1e4))

        # kernels
        kernelNoise = WhiteKernel(1, 'fixed')
        kernelLongTerm = C * RBF(10, 'fixed')
        kernelSeason = C * ExpSineSquared(length_scale=20, periodicity=1, length_scale_bounds='fixed', periodicity_bounds="fixed")
        kernelFree = C * RBF(sigma, 'fixed')

        # seasonal model
        kernel = kernelNoise + kernelLongTerm + kernelSeason
        #gps.append(GaussianProcessRegressor(kernel=kernel, alpha=0, normalize_y=True, n_restarts_optimizer=3, copy_X_train=False))

        # free model
        kernel = kernelNoise + kernelLongTerm + kernelFree #+ kernelSeason
        #gps.append(GaussianProcessRegressor(kernel=kernel, alpha=0, normalize_y=True, n_restarts_optimizer=3, copy_X_train=False))

        # free model SVR
        param_grid = {'gamma': [sigmaToGamma(days/365.) for days in range(90,365*2,30)]}
        gps.append(GridSearchCV(KernelRidge(alpha=alpha(1000), kernel='rbf'), cv=10, param_grid=param_grid, scoring='neg_mean_absolute_error'))


        validCube = numpy.array([landsat.images[id+'_qa'].cube[0] for id, landsat in mgrs.collections.items()]) <= 1
        #validCube[dyear[:,0] > 2016] = False
        srCubes = list(numpy.array([landsat.images[id+'_sr'].cube[i] for id, landsat in mgrs.collections.items()]) for i in range(6))
        srCubes.append(numpy.true_divide(srCubes[4-1]-srCubes[3-1], srCubes[4-1]+srCubes[3-1]) *10000 ) # NDVI

        def validPoints(i, sample, line):
            valid = validCube[:, line, sample]
            x = dyear[valid]
            y = srCubes[i][valid, line, sample]
            return x, y

        def validPointsScreened(i, sample, line):

            x2, y2 = validPoints(2-1, sample, line)
            y2_pred = sr_(x2, x2, y2)

            x5, y5 = validPoints(5-1, sample, line)
            y5_pred = sr_(x5, x5, y5)

            valid = numpy.logical_not((y2-y2_pred > 0.04*10000) + (y5-y5_pred < -0.04*10000))

            #valid[2:] = False

            x, y = validPoints(i, sample, line)
            return x[valid], y[valid]

        def sr(i, x, sample, line):
            x_train, y_train = validPointsScreened(i, sample, line)
            return sr_(x, x_train, y_train), residuals(x, x_train, y_train, y_train_pred=sr_(x_train, x_train, y_train))


        def residuals(x, x_train, y_train, y_train_pred):
            y_error = abs(y_train-y_train_pred)
            kernel = 1 * RBF(10, 'fixed') + WhiteKernel(1, 'fixed')
            gp = GaussianProcessRegressor(kernel=kernel, alpha=0, normalize_y=True, n_restarts_optimizer=3,
                                                copy_X_train=False)
            y_error_pred = gp.fit(x_train, y_error).predict(x)
            return y_error_pred

        def sr_(x, x_train, y_train):
            gp.fit(x_train, y_train)
            y_pred = gp.predict(x)#, return_std=False)
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

        lines, samples = validCube.shape[1:]
        for line in range(lines):
            for sample in range(samples):
                for bandIndex, bandName in enumerate(bandNames):
                    # if bandName != 'nir': continue
                    if bandIndex != 6: continue


                    #plt.figure(figsize=(15, 10))
                    for gp, format in zip(gps, ['b','b--']):
                        y_pred_grid, y_error_grid = sr(bandIndex, x_grid, sample, line)
                        plt.plot(x_grid, y_pred_grid, format, label=bandName+' Sigma='+str(int(gammaToSigma(gp.best_params_['gamma'])*365))+' days')
                        plt.fill_between(x_grid[:, 0], y_pred_grid - y_error_grid, y_pred_grid + y_error_grid,
                                         alpha=0.25, color='b')


                        #plt.scatter(x_grid, y_pred_grid, c='b', edgecolors='b')
                        print()
                        if isinstance(gp, GridSearchCV):
                            print(gp.best_params_)

                        #print(gp.kernel_)
                        #print(gp.log_marginal_likelihood(gp.kernel_.theta))

                        if 1: # plot NDVI calculated from red/nit fits
                            red = sr(3 - 1, x_grid, sample, line)[0]
                            nir = sr(4 - 1, x_grid, sample, line)[0]
                            ndvi_pred_grid = (nir-red)/(nir+red)*1e4
                            plt.plot(x_grid, ndvi_pred_grid, format.replace('b','g'), label=bandName+' from fitted RED, NIR')

                    #bpc_x, bpc_y = bestPixelCompositing(bandIndex, x_grid, sample, line)
                    #plt.plot(bpc_x, bpc_y, 'g')
                    plt.scatter(dyear, srCubes[bandIndex][:, line, sample], c='r', edgecolors='r')

                    x_valid, y_valid = validPoints(bandIndex, sample, line)
                    x_valid_screened, y_valid_screened = validPointsScreened(bandIndex, sample, line)
                    plt.scatter(x_valid, y_valid, c='y', edgecolors='y')
                    plt.scatter(x_valid_screened, y_valid_screened, c='k', edgecolors='k')

                    plt.xlim(x_grid.min(), x_grid.max())
                    plt.ylim(y_valid.min(), y_valid.max())
                    plt.ylim(0,10000)

                    #plt.xscale
                    plt.xlabel("Year")
                    plt.ylabel(bandName)
                    plt.title("Gaussian Process Regression")
                    plt.tight_layout()
                    #print
                    #print(gp.kernel_)
                    #print(gp1.log_marginal_likelihood(gp1.kernel_.theta))
                    plt.legend(loc="upper left", bbox_to_anchor=[0, 1],
                               ncol=1, shadow=True, title="Legend", fancybox=True)
                    plt.show()
                    #return
                    #plt.close()
        #self.outputs.imageCollectionList = imageCollectionListCopy

def test():

    workflow = TSFitting()
    workflow.infiles.mgrs = ImageCollectionList(r'C:\Work\data\gms\big\landsatXMGRS_GTiff_extracted\33\33UUT')
    workflow.outfiles.timeseries = ImageCollection(r'C:\Work\data\gms\big\timeseries\33\33UUT')
    workflow.controls.setNumThreads(1)
    workflow.controls.setOutputDriverGTiff()
    workflow.run()

def testKernel():

    f=2
    x = numpy.linspace(-numpy.pi*f, +numpy.pi*f, 1000)
    # k = exp(-2 sin(pi/p* d(xi,xj))/l)^2
    p = numpy.pi*2
    l = 1
    x = numpy.linspace(-3*l, +3*l, 1000)

    # sin
    y = numpy.exp(-2 *
                  numpy.sin(numpy.pi / p * abs(0-x))
                  / l) ** 2
    # RBF
    d = lambda a,b: abs(x-0)
    y = numpy.exp(-0.5 * d(x/l,0/l)**2)

    plt.plot(x,y)
    plt.show()

if __name__ == '__main__':
    tic()
    test()
    #testKernel()
    toc()