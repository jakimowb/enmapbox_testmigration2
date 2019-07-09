from hubflow.core import *
from sklearn.ensemble import RandomForestRegressor


def synthmixRegressionEnsemble(filename, classificationSample, targets, regressor, raster, runs, n,
                               mixingComplexities, classLikelihoods='equalized',
                               includeWithinclassMixtures=False, includeEndmember=False,
                               saveSamples=True, saveModels=True, savePredictions=True, saveMedian=True,
                               saveMean=True, saveIQR=True, saveStd=True, saveRGB=True, saveClassification=True,
                               clip=True, ui=None):

    # build ensemble

    directory = dirname(filename)
    prefix, ext = splitext(basename(filename))
    predictions = {target: list() for target in targets}
    results = list()

    classDefinition = ClassDefinition(names=[classificationSample.classification().classDefinition().name(label=target) for target in targets],
                                      colors=[classificationSample.classification().classDefinition().color(label=target) for target in targets])

    for run in range(runs):
        for target in targets:
            stamp = '_class{}_{}_run{}'.format(target, classificationSample.classification().classDefinition().name(label=target), run+1)
            if ui is not None:
                ui.uiProgressBar_.setRange(0, 100)
                ui.uiProgressBar_.setValue(float(run)/runs*100)
                ui.uiInfo_.setText('Calculate target {} in run {}'.format(classificationSample.classification().classDefinition().name(label=target), run+1))
                from PyQt5.QtWidgets import QApplication
                QApplication.processEvents()
            else:
                print(stamp)

            fractionSample = classificationSample.synthMix(
                filenameFeatures=join(directory, 'train', '{}_features{}{}'.format(prefix, stamp, ext)),
                filenameFractions=join(directory, 'train', '{}_fractions{}{}'.format(prefix, stamp, ext)),
                mixingComplexities=mixingComplexities, classLikelihoods=classLikelihoods,
                n=n, target=target,
                includeWithinclassMixtures=includeWithinclassMixtures, includeEndmember=includeEndmember)

            regressor.fit(sample=fractionSample)

            if saveModels:
                regressor.pickle(filename=join(directory, 'models', '{}_model{}.pkl'.format(prefix, stamp)))

            if savePredictions or saveMean or saveStd or saveMedian or saveIQR:
                vsimem = '/vsimem/' if not savePredictions else ''
                prediction = regressor.predict(filename=vsimem + join(directory, 'predictions', '{}_prediction{}{}'.format(prefix, stamp, ext)),
                                               raster=raster,
                                               emitFileCreated=False)
                predictions[target].append(prediction)

            fractionSample.regression().dataset().close()
            fractionSample.raster().dataset().close()


    # aggregate

    if ui is not None:
        ui.uiProgressBar_.setValue(99)
        ui.uiInfo_.setText('Calculate aggregations')
        QApplication.processEvents()

    keys = list()
    if saveMedian: keys.append('median')
    if saveMean: keys.append('mean')
    if saveIQR: keys.append('iqr')
    if saveStd: keys.append('std')

    if len(keys) > 0:
        applier = Applier()
        for target in predictions:
            vrtFilename = '/vsimem/synthmixapp/{}.vrt'.format(target)
            print(vrtFilename)
            createVRTDataset(rasterDatasetsOrFilenames=[raster.filename() for raster in predictions[target]],
                             filename=vrtFilename,
                             separate=True)
            applier.setFlowRaster(name=str(target), raster=Raster(vrtFilename))

        for key in keys:
            filename = join(directory, '{}_{}{}'.format(prefix, key, ext))
            applier.setOutputRaster(name=key, filename=filename)
            results.append(filename)
        applier.apply(operatorType=Aggregate, predictions=predictions, keys=keys, clip=clip, classDefinition=classDefinition)

    # RGB

    if saveRGB:
        keys = list()
        if saveMean: keys.append('mean')
        if saveMedian: keys.append('median')
        for key in keys:
            fraction = Fraction(filename=join(directory, '{}_{}{}'.format(prefix, key, ext)),
                                classDefinition=classDefinition)
            results.append(fraction.filename())
            rgb = fraction.asClassColorRGBRaster(filename=join(directory, '{}_{}_rgb{}'.format(prefix, key, ext)))
            results.append(rgb.filename())

    # Classification

    if saveClassification:
        keys = list()
        if saveMean: keys.append('mean')
        if saveMedian: keys.append('median')
        for key in keys:
            fraction = Fraction(filename=join(directory, '{}_{}{}'.format(prefix, key, ext)),
                                classDefinition=classDefinition)
            results.append(fraction.filename())
            classification = Classification.fromClassification(filename=join(directory, '{}_{}_classification{}'.format(prefix, key, ext)),
                                                               classification=fraction)
            results.append(classification.filename())

    # open files
    from enmapbox.gui.enmapboxgui import EnMAPBox
    if EnMAPBox.instance() is not None:
        EnMAPBox.instance().addSources(sourceList=results)

    # clean up
    import shutil
    # Deleting the predictions does not work!??? Put all predictions into vsimem, see above
    # if not savePredictions:
    #    for l in predictions.values():
    #        for prediction in l:
    #            prediction.dataset().close()
    #    shutil.rmtree(join(directory, 'predictions'))

    if not saveSamples:
        shutil.rmtree(join(directory, 'train'))

    if ui is not None:
        ui.uiProgressBar_.setValue(0)
        ui.uiInfo_.setText('Completed successfully!')
        QApplication.processEvents()



class Aggregate(ApplierOperator):
    def ufunc(self, predictions, keys, clip, classDefinition):
        results = {key: list() for key in keys}

        # reduce over runs and stack targets
        for target in predictions:
            #array = self.flowRasterArray(name=str(target), raster=RasterStack(predictions[target]))
            array = self.inputRaster.raster(key=str(target)).array()
            if clip:
                np.clip(array, a_min=0, a_max=1, out=array)
            if 'mean' in keys:
                results['mean'].append(np.mean(array, axis=0))
            if 'std' in keys:
                results['std'].append(np.std(array, axis=0))
            if 'median' in keys and 'iqr' in keys:
                p25, median, p75 = np.percentile(array, q=(25, 50, 75), axis=0)
                results['median'].append(median)
                results['iqr'].append(p75 - p25)
            elif 'median' in keys and 'iqr' not in keys:
                results['median'].append(np.median(array, axis=0))
            elif 'median' not in keys and 'iqr' in keys:
                p25, p75 = np.percentile(array, q=(25, 75), axis=0)
                results['iqr'].append(p75 - p25)

        for key in keys:
            raster = self.outputRaster.raster(key=key)
            raster.setArray(results[key])

            if key in ['mean', 'median']:
                MetadataEditor.setFractionDefinition(rasterDataset=raster, classDefinition=classDefinition)

            for key in ['iqr', 'std']:
                if key in keys:
                    MetadataEditor.setBandNames(rasterDataset=raster, bandNames=classDefinition.names())


def test():
    import enmapboxtestdata
    library = EnviSpectralLibrary(filename=enmapboxtestdata.library)
    labels = Classification.fromEnviSpectralLibrary(filename='/vsimem/synthmixRegressionEnsemble/labels.bsq',
                                                    library=library, attribute='level_2')

    synthmixRegressionEnsemble(filename=r'c:\output\synthmixRegressionEnsemble\ar.bsq',
                               classificationSample=ClassificationSample(raster=library.raster(), classification=labels),
                               targets=labels.classDefinition().labels()[0:2],
                               regressor=Regressor(sklEstimator=RandomForestRegressor(n_estimators=10, n_jobs=-1)),
                               raster=Raster(filename=enmapboxtestdata.enmap),
                               runs=3, n=100,
                               mixingComplexities={2: 0.5, 3: 0.5},
                               classLikelihoods='equalized',
                               includeWithinclassMixtures=False,
                               includeEndmember=False,
                               saveSamples=not False, saveModels=not False, savePredictions=not False)

if __name__ == '__main__':
    test()

