import json
from collections import defaultdict
from dataclasses import dataclass
from os import makedirs
from os.path import exists, dirname, join
from typing import Dict, Any, List, Tuple, Iterable

import numpy as np
from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsVectorLayer, QgsRasterLayer, QgsUnitTypes,
                        QgsCategorizedSymbolRenderer, QgsProcessingException)

from enmapbox.externals.qps.speclib.core import SpectralLibrary
from enmapboxprocessing.algorithm.prepareclassificationdatasetfromcategorizedlibraryalgorithm import \
    PrepareClassificationDatasetFromCategorizedLibraryAlgorithm
from enmapboxprocessing.algorithm.rasterizecategorizedvectoralgorithm import RasterizeCategorizedVectorAlgorithm
from enmapboxprocessing.algorithm.translatecategorizedrasteralgorithm import TranslateCategorizedRasterAlgorithm
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.rasterreader import RasterReader
from enmapboxprocessing.reportwriter import HtmlReportWriter, CsvReportWriter, MultiReportWriter
from enmapboxprocessing.typing import ClassifierDump, Category, checkSampleShape, RegressionDump
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class SynthMixAlgorithm(EnMAPProcessingAlgorithm):
    P_DATASET, _DATASET = 'dataset', 'Classification dataset'
    P_N, _N = 'n', 'Number of mixtures per class'
    P_INCLUDE_ENDMEMBER, _INCLUDE_ENDMEMBER = 'includeEndmember', 'Include original endmembers'
    P_MIXING_LIKELIHOODS, _MIXING_LIKELIHOODS = 'mixingLikelihoods', 'Mixing complexity likelihoods'
    P_ALLOW_WITHINCLASS_MIXTURES, _ALLOW_WITHINCLASS_MIXTURES = 'allowWithinClassMixtures', 'Allow within-class mixtures'
    P_CLASS_LIKELIHOODS, _CLASS_LIKELIHOODS = 'classLikelihoods', 'Class likelihoods'
    P_OUTPUT_DATASET, _OUTPUT_DATASET = 'outputFolder', 'Output folder'

    @classmethod
    def displayName(cls) -> str:
        return 'SynthMix'

    def shortDescription(self) -> str:
        return 'Create synthetically mixed regression datasets, one for each category. ' \
               'Results are stored as <category.name>.pkl files inside the destination folder.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._DATASET, 'A classification dataset with spectral endmembers used for synthetical mixing.'),
            (self._N, 'Number of mixtures per class'),
            (self._INCLUDE_ENDMEMBER, 'Whether to include the original library spectra into the dataset.'),
            (self._MIXING_LIKELIHOODS, 'A list of likelihoods for using 2, 3, 4, ... endmember mixing models. '
                                       'Trailing 0 likelihoods can be skipped. The default values of 0.5, 0.5,'
                                       'results in 50% 2-endmember and 50% 3-endmember models.'),
            (self._ALLOW_WITHINCLASS_MIXTURES, 'Whether to allow mixtures with profiles belonging to the same class.'),
            (self._CLASS_LIKELIHOODS, 'A list of likelihoods for drawing profiles from each class. '
                                      'If not specified, class likelihoods are proportional to the class size.'),
            (self._OUTPUT_DATASET, self.FolderDestination)
        ]

    def group(self):
        return Group.Test.value + Group.DatasetCreation.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterFile(self.P_DATASET, self._DATASET)
        self.addParameterInt(self.P_N, self._N, None, False, 0)
        self.addParameterBoolean(self.P_INCLUDE_ENDMEMBER, self._INCLUDE_ENDMEMBER, True)
        self.addParameterString(self.P_MIXING_LIKELIHOODS, self._MIXING_LIKELIHOODS, '0.5, 0.5', False, True)
        self.addParameterBoolean(self.P_ALLOW_WITHINCLASS_MIXTURES, self._ALLOW_WITHINCLASS_MIXTURES, True)
        self.addParameterString(self.P_CLASS_LIKELIHOODS, self._CLASS_LIKELIHOODS, None, False, True)
        self.addParameterFolderDestination(self.P_OUTPUT_DATASET, self._OUTPUT_DATASET)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        filenameDataset = self.parameterAsFile(parameters, self.P_DATASET, context)
        self.n = self.parameterAsInt(parameters, self.P_N, context)
        self.includeEndmember = self.parameterAsBoolean(parameters, self.P_INCLUDE_ENDMEMBER, context)
        self.mixingLikelihoods = self.parameterAsValues(parameters, self.P_MIXING_LIKELIHOODS, context)
        self.allowWithinClassMixtures = self.parameterAsBoolean(parameters, self.P_ALLOW_WITHINCLASS_MIXTURES, context)
        self.classLikelihoods = self.parameterAsValues(parameters, self.P_CLASS_LIKELIHOODS, context)
        foldername = self.parameterAsFileOutput(parameters, self.P_OUTPUT_DATASET, context)

        with open(join(foldername, 'processing.log'), 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            dump = ClassifierDump(**Utils.pickleLoad(filenameDataset))
            self.X = dump.X
            self.y = dump.y
            self.categories = dump.categories
            feedback.pushInfo(f'Load classification dataset: X=array{list(self.X.shape)} y=array{list(self.y.shape)} categories={[c.name for c in self.categories]}')

            if self.classLikelihoods is None:
                self.classLikelihoods = list()
                for category in self.categories:
                    self.classLikelihoods.append(np.average(self.y == category.value))

            for target in self.categories:
                X, y = self.mixTarget(target)

                checkSampleShape(X, y, raise_=True)

                features = [f'Band {i + 1}' for i in range(X.shape[1])]
                dump = RegressionDump(targets=[target.name], features=features, X=X, y=y)
                dumpDict = dump.__dict__
                Utils.pickleDump(dumpDict, filename)

            result = {self.P_OUTPUT_FOLDER: foldername}
            self.toc(feedback, result)

        return result

    def mixTarget(self, target: Category):

        targetIndex = self.categories.index(target)
        features, labels = self.X.T, self.y.flatten()
        classes = len(self.categories)
        classLikelihoods = {category.value: v for category, v in zip(self.categories, self.classLikelihoods)}
        mixingComplexities = {i: v for i, v in enumerate(self.mixingLikelihoods, 2)}
        targetRange = [0, 1]

        # cache label indices and setup 0%/100% fractions from class labels
        indices = dict()
        zeroOneFractions = np.zeros((classes, features.shape[1]), dtype=np.float32)
        for i, category in enumerate(self.categories):
            indices[category.value] = np.where(labels == category.value)[0]
            zeroOneFractions[i, indices[category.value]] = 1.

        # create mixtures
        mixtures = list()
        fractions = list()

        classLikelihoods2 = {k: v / (1 - classLikelihoods[target.value])
                             for k, v in classLikelihoods.items()
                             if k != target.value}
        for i in range(self.n):
            complexity = np.random.choice(list(mixingComplexities.keys()), p=list(mixingComplexities.values()))
            drawnLabels = [target.value]

            if self.allowWithinClassMixtures:
                drawnLabels.extend(np.random.choice(list(classLikelihoods.keys()), size=complexity - 1, replace=True,
                    p=list(classLikelihoods.values())))
            else:
                drawnLabels.extend(np.random.choice(list(classLikelihoods2.keys()), size=complexity - 1, replace=False,
                    p=list(classLikelihoods2.values())))

            drawnIndices = [np.random.choice(indices[label]) for label in drawnLabels]
            drawnFeatures = features[:, drawnIndices]
            drawnFractions = zeroOneFractions[:, drawnIndices]

            randomWeights = list()
            for i in range(complexity - 1):
                if i == 0:
                    weight = np.random.random() * (targetRange[1] - targetRange[0]) + targetRange[0]
                else:
                    weight = np.random.random() * (1. - sum(randomWeights))
                randomWeights.append(weight)
            randomWeights.append(1. - sum(randomWeights))

            assert sum(randomWeights) == 1.
            mixtures.append(np.sum(drawnFeatures * randomWeights, axis=1))
            fractions.append(np.sum(drawnFractions * randomWeights, axis=1)[targetIndex])

        if self.includeEndmember:
            mixtures.extend(features.T)
            fractions.extend(np.float32(labels == target.value)[0])  # 1. for target class, 0. for the rest

        X = np.array(mixtures, dtype=np.float32)
        y = np.array(fractions, dtype=np.float32)[None]

        return X, y
