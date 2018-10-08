=======
Classes
=======

Raster Maps
-----------


Raster
~~~~~~

- :class:`hubflow.core.Raster`:
   + :meth:`~hubflow.core.Raster.applyMask` :meth:`~hubflow.core.Raster.applySpatial` :meth:`~hubflow.core.Raster.array` :meth:`~hubflow.core.Raster.asMask` :meth:`~hubflow.core.Raster.convolve` :meth:`~hubflow.core.Raster.dataset` :meth:`~hubflow.core.Raster.dtype` :meth:`~hubflow.core.Raster.filename` :meth:`~hubflow.core.Raster.fromArray` :meth:`~hubflow.core.Raster.fromRasterDataset` :meth:`~hubflow.core.Raster.fromVector` :meth:`~hubflow.core.Raster.grid` :meth:`~hubflow.core.Raster.metadataDict` :meth:`~hubflow.core.Raster.metadataFWHM` :meth:`~hubflow.core.Raster.metadataWavelength` :meth:`~hubflow.core.Raster.noDataValue` :meth:`~hubflow.core.Raster.noDataValues` :meth:`~hubflow.core.Raster.plotCategoryBand` :meth:`~hubflow.core.Raster.plotMultibandColor` :meth:`~hubflow.core.Raster.plotSinglebandGrey` :meth:`~hubflow.core.Raster.plotZProfile` :meth:`~hubflow.core.Raster.readAsArray` :meth:`~hubflow.core.Raster.resample` :meth:`~hubflow.core.Raster.scatterMatrix` :meth:`~hubflow.core.Raster.sensorDefinition` :meth:`~hubflow.core.Raster.shape` :meth:`~hubflow.core.Raster.statistics` :meth:`~hubflow.core.Raster.uniqueValues`


.. autoclass:: hubflow.core.Raster
   :members:
   :show-inheritance:
   :undoc-members:

Mask
~~~~

- :class:`hubflow.core.Mask`:
   + :meth:`~hubflow.core.Mask.indices` :meth:`~hubflow.core.Mask.invert` :meth:`~hubflow.core.Mask.minOverallCoverage` :meth:`~hubflow.core.Mask.noDataValues` :meth:`~hubflow.core.Mask.resample`


.. autoclass:: hubflow.core.Mask
   :members:
   :show-inheritance:
   :undoc-members:

Classification
~~~~~~~~~~~~~~

- :class:`hubflow.core.Classification`:
   + :meth:`~hubflow.core.Classification.asMask` :meth:`~hubflow.core.Classification.classDefinition` :meth:`~hubflow.core.Classification.dtype` :meth:`~hubflow.core.Classification.fromArray` :meth:`~hubflow.core.Classification.fromClassification` :meth:`~hubflow.core.Classification.fromFraction` :meth:`~hubflow.core.Classification.fromRasterAndFunction` :meth:`~hubflow.core.Classification.minDominantCoverage` :meth:`~hubflow.core.Classification.minOverallCoverage` :meth:`~hubflow.core.Classification.noDataValues` :meth:`~hubflow.core.Classification.plot` :meth:`~hubflow.core.Classification.reclassify` :meth:`~hubflow.core.Classification.resample` :meth:`~hubflow.core.Classification.statistics`


.. autoclass:: hubflow.core.Classification
   :members:
   :show-inheritance:
   :undoc-members:

Fraction
~~~~~~~~

- :class:`hubflow.core.Fraction`:
   + :meth:`~hubflow.core.Fraction.asClassColorRGBRaster` :meth:`~hubflow.core.Fraction.classDefinition` :meth:`~hubflow.core.Fraction.fromClassification` :meth:`~hubflow.core.Fraction.fromENVISpectralLibrary` :meth:`~hubflow.core.Fraction.minDominantCoverage` :meth:`~hubflow.core.Fraction.minOverallCoverage` :meth:`~hubflow.core.Fraction.noDataValues` :meth:`~hubflow.core.Fraction.resample` :meth:`~hubflow.core.Fraction.subsetClasses` :meth:`~hubflow.core.Fraction.subsetClassesByName`


.. autoclass:: hubflow.core.Fraction
   :members:
   :show-inheritance:
   :undoc-members:

Regression
~~~~~~~~~~

- :class:`hubflow.core.Regression`:
   + :meth:`~hubflow.core.Regression.asMask` :meth:`~hubflow.core.Regression.minOverallCoverage` :meth:`~hubflow.core.Regression.noDataValues` :meth:`~hubflow.core.Regression.outputNames` :meth:`~hubflow.core.Regression.outputs` :meth:`~hubflow.core.Regression.resample`


.. autoclass:: hubflow.core.Regression
   :members:
   :show-inheritance:
   :undoc-members:

RasterStack
~~~~~~~~~~~

- :class:`hubflow.core.RasterStack`:
   + :meth:`~hubflow.core.RasterStack.raster` :meth:`~hubflow.core.RasterStack.rasters`


.. autoclass:: hubflow.core.RasterStack
   :members:
   :show-inheritance:
   :undoc-members:

Vector Maps
-----------


Vector
~~~~~~

- :class:`hubflow.core.Vector`:
   + :meth:`~hubflow.core.Vector.allTouched` :meth:`~hubflow.core.Vector.burnAttribute` :meth:`~hubflow.core.Vector.burnValue` :meth:`~hubflow.core.Vector.dataset` :meth:`~hubflow.core.Vector.dtype` :meth:`~hubflow.core.Vector.filename` :meth:`~hubflow.core.Vector.filterSQL` :meth:`~hubflow.core.Vector.fromPoints` :meth:`~hubflow.core.Vector.fromRandomPointsFromClassification` :meth:`~hubflow.core.Vector.fromRandomPointsFromMask` :meth:`~hubflow.core.Vector.fromVectorDataset` :meth:`~hubflow.core.Vector.grid` :meth:`~hubflow.core.Vector.initValue` :meth:`~hubflow.core.Vector.layer` :meth:`~hubflow.core.Vector.noDataValue` :meth:`~hubflow.core.Vector.projection` :meth:`~hubflow.core.Vector.spatialExtent` :meth:`~hubflow.core.Vector.uniqueValues`


.. autoclass:: hubflow.core.Vector
   :members:
   :show-inheritance:
   :undoc-members:

VectorMask
~~~~~~~~~~

- :class:`hubflow.core.VectorMask`:
   + :meth:`~hubflow.core.VectorMask.invert` :meth:`~hubflow.core.VectorMask.kwargs`


.. autoclass:: hubflow.core.VectorMask
   :members:
   :show-inheritance:
   :undoc-members:

VectorClassification
~~~~~~~~~~~~~~~~~~~~

- :class:`hubflow.core.VectorClassification`:
   + :meth:`~hubflow.core.VectorClassification.classAttribute` :meth:`~hubflow.core.VectorClassification.classDefinition` :meth:`~hubflow.core.VectorClassification.minDominantCoverage` :meth:`~hubflow.core.VectorClassification.minOverallCoverage` :meth:`~hubflow.core.VectorClassification.oversampling`


.. autoclass:: hubflow.core.VectorClassification
   :members:
   :show-inheritance:
   :undoc-members:

Samples
-------


ClassificationSample
~~~~~~~~~~~~~~~~~~~~

- :class:`hubflow.core.ClassificationSample`:
   + :meth:`~hubflow.core.ClassificationSample.classification` :meth:`~hubflow.core.ClassificationSample.masks` :meth:`~hubflow.core.ClassificationSample.synthMix` :meth:`~hubflow.core.ClassificationSample.synthMix2`


.. autoclass:: hubflow.core.ClassificationSample
   :members:
   :show-inheritance:
   :undoc-members:

FractionSample
~~~~~~~~~~~~~~

- :class:`hubflow.core.FractionSample`:
   + :meth:`~hubflow.core.FractionSample.fraction`


.. autoclass:: hubflow.core.FractionSample
   :members:
   :show-inheritance:
   :undoc-members:

RegressionSample
~~~~~~~~~~~~~~~~

- :class:`hubflow.core.RegressionSample`:
   + :meth:`~hubflow.core.RegressionSample.masks` :meth:`~hubflow.core.RegressionSample.regression`


.. autoclass:: hubflow.core.RegressionSample
   :members:
   :show-inheritance:
   :undoc-members:

MapCollection
~~~~~~~~~~~~~

- :class:`hubflow.core.MapCollection`:
   + :meth:`~hubflow.core.MapCollection.extractAsArray` :meth:`~hubflow.core.MapCollection.extractAsRaster` :meth:`~hubflow.core.MapCollection.maps`


.. autoclass:: hubflow.core.MapCollection
   :members:
   :show-inheritance:
   :undoc-members:

Estimators
----------


Classifier
~~~~~~~~~~

- :class:`hubflow.core.Classifier`:
   + :meth:`~hubflow.core.Classifier.PREDICT_TYPE` :meth:`~hubflow.core.Classifier.SAMPLE_TYPE` :meth:`~hubflow.core.Classifier.fit` :meth:`~hubflow.core.Classifier.predict` :meth:`~hubflow.core.Classifier.predictProbability`


.. autoclass:: hubflow.core.Classifier
   :members:
   :show-inheritance:
   :undoc-members:

Regressor
~~~~~~~~~

- :class:`hubflow.core.Regressor`:
   + :meth:`~hubflow.core.Regressor.PREDICT_TYPE` :meth:`~hubflow.core.Regressor.SAMPLE_TYPE` :meth:`~hubflow.core.Regressor.fit` :meth:`~hubflow.core.Regressor.predict`


.. autoclass:: hubflow.core.Regressor
   :members:
   :show-inheritance:
   :undoc-members:

Clusterer
~~~~~~~~~

- :class:`hubflow.core.Clusterer`:
   + :meth:`~hubflow.core.Clusterer.PREDICT_TYPE` :meth:`~hubflow.core.Clusterer.SAMPLE_TYPE` :meth:`~hubflow.core.Clusterer.classDefinition` :meth:`~hubflow.core.Clusterer.fit` :meth:`~hubflow.core.Clusterer.predict` :meth:`~hubflow.core.Clusterer.transform`


.. autoclass:: hubflow.core.Clusterer
   :members:
   :show-inheritance:
   :undoc-members:

Transformer
~~~~~~~~~~~

- :class:`hubflow.core.Transformer`:
   + :meth:`~hubflow.core.Transformer.PREDICT_TYPE` :meth:`~hubflow.core.Transformer.SAMPLE_TYPE` :meth:`~hubflow.core.Transformer.fit` :meth:`~hubflow.core.Transformer.inverseTransform` :meth:`~hubflow.core.Transformer.transform`


.. autoclass:: hubflow.core.Transformer
   :members:
   :show-inheritance:
   :undoc-members:

Accuracy Assessment
-------------------


ClassificationPerformance
~~~~~~~~~~~~~~~~~~~~~~~~~

- :class:`hubflow.core.ClassificationPerformance`:
   + :meth:`~hubflow.core.ClassificationPerformance.report`


.. autoclass:: hubflow.core.ClassificationPerformance
   :members:
   :show-inheritance:
   :undoc-members:

RegressionPerformance
~~~~~~~~~~~~~~~~~~~~~

- :class:`hubflow.core.RegressionPerformance`:
   + :meth:`~hubflow.core.RegressionPerformance.fromRaster` :meth:`~hubflow.core.RegressionPerformance.report`


.. autoclass:: hubflow.core.RegressionPerformance
   :members:
   :show-inheritance:
   :undoc-members:

FractionPerformance
~~~~~~~~~~~~~~~~~~~

- :class:`hubflow.core.FractionPerformance`:
   + :meth:`~hubflow.core.FractionPerformance.fromRaster` :meth:`~hubflow.core.FractionPerformance.report`


.. autoclass:: hubflow.core.FractionPerformance
   :members:
   :show-inheritance:
   :undoc-members:

ClusteringPerformance
~~~~~~~~~~~~~~~~~~~~~

- :class:`hubflow.core.ClusteringPerformance`:
   + :meth:`~hubflow.core.ClusteringPerformance.report`


.. autoclass:: hubflow.core.ClusteringPerformance
   :members:
   :show-inheritance:
   :undoc-members:

Miscellaneous
-------------


ClassDefinition
~~~~~~~~~~~~~~~

- :class:`hubflow.core.ClassDefinition`:
   + :meth:`~hubflow.core.ClassDefinition.classes` :meth:`~hubflow.core.ClassDefinition.color` :meth:`~hubflow.core.ClassDefinition.colorByName` :meth:`~hubflow.core.ClassDefinition.colors` :meth:`~hubflow.core.ClassDefinition.colorsFlatRGB` :meth:`~hubflow.core.ClassDefinition.dtype` :meth:`~hubflow.core.ClassDefinition.equal` :meth:`~hubflow.core.ClassDefinition.labelByName` :meth:`~hubflow.core.ClassDefinition.labels` :meth:`~hubflow.core.ClassDefinition.name` :meth:`~hubflow.core.ClassDefinition.names`


.. autoclass:: hubflow.core.ClassDefinition
   :members:
   :show-inheritance:
   :undoc-members:

SensorDefinition
~~~~~~~~~~~~~~~~

- :class:`hubflow.core.SensorDefinition`:
   + :meth:`~hubflow.core.SensorDefinition.fromENVISpectralLibrary` :meth:`~hubflow.core.SensorDefinition.plot` :meth:`~hubflow.core.SensorDefinition.resampleProfiles` :meth:`~hubflow.core.SensorDefinition.resampleRaster` :meth:`~hubflow.core.SensorDefinition.wavebandCount` :meth:`~hubflow.core.SensorDefinition.wavebandDefinition` :meth:`~hubflow.core.SensorDefinition.wavebandDefinitions`


.. autoclass:: hubflow.core.SensorDefinition
   :members:
   :show-inheritance:
   :undoc-members:

WavebandDefinition
~~~~~~~~~~~~~~~~~~

- :class:`hubflow.core.WavebandDefinition`:
   + :meth:`~hubflow.core.WavebandDefinition.center` :meth:`~hubflow.core.WavebandDefinition.fwhm` :meth:`~hubflow.core.WavebandDefinition.name` :meth:`~hubflow.core.WavebandDefinition.plot` :meth:`~hubflow.core.WavebandDefinition.resamplingWeights` :meth:`~hubflow.core.WavebandDefinition.responses`


.. autoclass:: hubflow.core.WavebandDefinition
   :members:
   :show-inheritance:
   :undoc-members:

MetadataEditor
~~~~~~~~~~~~~~

- :class:`hubflow.core.MetadataEditor`:
   + :meth:`~hubflow.core.MetadataEditor.bandCharacteristics` :meth:`~hubflow.core.MetadataEditor.bandNames` :meth:`~hubflow.core.MetadataEditor.setBandCharacteristics` :meth:`~hubflow.core.MetadataEditor.setBandNames` :meth:`~hubflow.core.MetadataEditor.setFractionDefinition` :meth:`~hubflow.core.MetadataEditor.setRegressionDefinition`


.. autoclass:: hubflow.core.MetadataEditor
   :members:
   :show-inheritance:
   :undoc-members:

Applier
-------


Applier
~~~~~~~

- :class:`hubflow.core.Applier`:
   + :meth:`~hubflow.core.Applier.apply` :meth:`~hubflow.core.Applier.setFlowClassification` :meth:`~hubflow.core.Applier.setFlowFraction` :meth:`~hubflow.core.Applier.setFlowInput` :meth:`~hubflow.core.Applier.setFlowMask` :meth:`~hubflow.core.Applier.setFlowMasks` :meth:`~hubflow.core.Applier.setFlowRaster` :meth:`~hubflow.core.Applier.setFlowRegression` :meth:`~hubflow.core.Applier.setFlowVector` :meth:`~hubflow.core.Applier.setOutputRaster`


.. autoclass:: hubflow.core.Applier
   :members:
   :show-inheritance:
   :undoc-members:

ApplierOperator
~~~~~~~~~~~~~~~

- :class:`hubflow.core.ApplierOperator`:
   + :meth:`~hubflow.core.ApplierOperator.flowClassificationArray` :meth:`~hubflow.core.ApplierOperator.flowFractionArray` :meth:`~hubflow.core.ApplierOperator.flowInputArray` :meth:`~hubflow.core.ApplierOperator.flowInputDType` :meth:`~hubflow.core.ApplierOperator.flowInputZSize` :meth:`~hubflow.core.ApplierOperator.flowMaskArray` :meth:`~hubflow.core.ApplierOperator.flowMasksArray` :meth:`~hubflow.core.ApplierOperator.flowRasterArray` :meth:`~hubflow.core.ApplierOperator.flowRegressionArray` :meth:`~hubflow.core.ApplierOperator.flowVectorArray` :meth:`~hubflow.core.ApplierOperator.maskFromArray` :meth:`~hubflow.core.ApplierOperator.maskFromBandArray` :meth:`~hubflow.core.ApplierOperator.maskFromFractionArray` :meth:`~hubflow.core.ApplierOperator.setFlowMetadataBandNames` :meth:`~hubflow.core.ApplierOperator.setFlowMetadataClassDefinition` :meth:`~hubflow.core.ApplierOperator.setFlowMetadataFractionDefinition` :meth:`~hubflow.core.ApplierOperator.setFlowMetadataNoDataValues` :meth:`~hubflow.core.ApplierOperator.setFlowMetadataRegressionDefinition` :meth:`~hubflow.core.ApplierOperator.setFlowMetadataSensorDefinition`


.. autoclass:: hubflow.core.ApplierOperator
   :members:
   :show-inheritance:
   :undoc-members:
