from hubflow.core import *

text = list()
text.append('''
=======
Classes
=======
''')

def addClasses(classes, title):
    text.append('\n{}\n{}\n\n'.format(title, '-'*len(title)))

    for cls in classes:

        text.append('\n{}\n{}\n\n'.format(cls.__name__, '~'*len(cls.__name__) ))

        text.append('- :class:`{}.{}`:\n'.format(cls.__module__, cls.__name__))

        text2 = ('   +')
        for k in sorted(cls.__dict__.keys()):
            v = cls.__dict__[k]
            if k.startswith('_'): continue
            if callable(v) or isinstance(v, classmethod):
                text2 += ' :meth:`~{}.{}.{}`'.format(cls.__module__, cls.__name__, k)
        text2 += '\n\n'
        text.append(text2)

        text.append('''
.. autoclass:: {}.{}
   :members:
   :show-inheritance:
   :undoc-members:
'''.format(cls.__module__, cls.__name__))


addClasses(classes=[Raster, Mask, Classification, Fraction, Regression, RasterStack], title='Raster Maps')
addClasses(classes=[Vector, VectorMask, VectorClassification], title='Vector Maps')
addClasses(classes=[ClassificationSample, FractionSample, RegressionSample, MapCollection], title='Samples')
addClasses(classes=[Classifier, Regressor, Clusterer, Transformer], title='Estimators')
addClasses(classes=[ClassificationPerformance, RegressionPerformance, ClusteringPerformance], title='Accuracy Assessment')
addClasses(classes=[ClassDefinition, SensorDefinition, WavebandDefinition, MetadataEditor], title='Miscellaneous')
addClasses(classes=[Applier, ApplierOperator], title='Applier')

with open('hubflow_core.rst', 'w') as f:
    f.writelines(text)

