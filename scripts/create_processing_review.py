from qgis._core import QgsProcessingParameterDefinition, QgsProcessingDestinationParameter, QgsProcessingAlgorithm

from enmapboxgeoalgorithms.algorithms import ALGORITHMS
from enmapboxprocessing.utils import Utils

groups = dict()
for alg in ALGORITHMS:
    alg.initAlgorithm()
    if alg.group() not in groups:
        groups[alg.group()] = dict()
    groups[alg.group()][alg.displayName()] = alg

result = dict()
for gkey in sorted(groups.keys()):
    result[gkey] = dict()
    for akey in groups[gkey]:
        result[gkey][akey] = list()
        alg = groups[gkey][akey]
        assert isinstance(alg, QgsProcessingAlgorithm)
        for pd in alg.parameterDefinitions():
            assert isinstance(pd, QgsProcessingParameterDefinition)
            result[gkey][akey].append(pd.description())
Utils.jsonDump(result, 'algos.json')