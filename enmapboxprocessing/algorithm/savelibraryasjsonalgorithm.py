from typing import Dict, Any, List, Tuple

from qgis._core import (QgsProcessingContext, QgsProcessingFeedback, QgsField, QgsFeature)

from enmapbox.qgispluginsupport.qps.speclib.core import is_profile_field
from enmapbox.qgispluginsupport.qps.speclib.core.spectralprofile import SpectralProfile
from enmapboxprocessing.enmapalgorithm import EnMAPProcessingAlgorithm, Group
from enmapboxprocessing.utils import Utils
from typeguard import typechecked


@typechecked
class SaveLibraryAsJsonAlgorithm(EnMAPProcessingAlgorithm):
    P_LIBRARY, _LIBRARY = 'library', 'Spectral library'
    P_OUTPUT_FILE, _OUTPUT_FILE = 'outputFile', 'Output file'

    @classmethod
    def displayName(cls) -> str:
        return 'Save spectral library as JSON file'

    def shortDescription(self) -> str:
        return 'Save a spectral library as a human-readable JSON text file.'

    def helpParameters(self) -> List[Tuple[str, str]]:
        return [
            (self._LIBRARY, 'The spectral library to be saved as JSON text file.'),
            (self._OUTPUT_FILE, self.JsonFileDestination)
        ]

    def group(self):
        return Group.Test.value + Group.ExportData.value

    def initAlgorithm(self, configuration: Dict[str, Any] = None):
        self.addParameterVectorLayer(self.P_LIBRARY, self._LIBRARY)
        self.addParameterFileDestination(self.P_OUTPUT_FILE, self._OUTPUT_FILE, self.JsonFileFilter)

    def processAlgorithm(
            self, parameters: Dict[str, Any], context: QgsProcessingContext, feedback: QgsProcessingFeedback
    ) -> Dict[str, Any]:
        library = self.parameterAsVectorLayer(parameters, self.P_LIBRARY, context)
        filename = self.parameterAsFileOutput(parameters, self.P_OUTPUT_FILE, context)

        with open(filename + '.log', 'w') as logfile:
            feedback, feedback2 = self.createLoggingFeedback(feedback, logfile)
            self.tic(feedback, parameters, context)

            # open library
            jsonDump = list()
            n = library.featureCount()
            feature: QgsFeature
            for i, feature in enumerate(library.getFeatures()):
                feedback.setProgress(i / n * 100)
                attributes = dict()
                field: QgsField
                for fieldIndex, field in enumerate(feature.fields()):
                    if is_profile_field(field):
                        spectralProfile = SpectralProfile.fromQgsFeature(feature, field)
                        attributes[field.name()] = spectralProfile.values()
                    else:
                        attributes[field.name()] = feature.attribute(fieldIndex)
                jsonDump.append(attributes)

            Utils.jsonDump(jsonDump, filename)

            result = {self.P_OUTPUT_FILE: filename}
            self.toc(feedback, result)
        return result
