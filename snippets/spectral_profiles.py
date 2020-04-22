from enmapbox.testing import initQgisApplication, TestObjects
from enmapbox.gui import SpectralProfile, SpectralLibrary
from qgis.core import QgsFeature
app = initQgisApplication()

speclib = TestObjects.createSpectralLibrary(50)

assert isinstance(speclib, SpectralLibrary)

for profile in speclib:
    assert isinstance(profile, SpectralProfile)
    assert isinstance(profile, QgsFeature) #<- This

    print('ID:{} "{}"'.format(profile.id(), profile.name()))
    #profile values
    xValues = profile.xValues() # band index or, if defined, wavelength
    yValues = profile.yValues() # reflectances
    yUnit = profile.yUnit() #
    xUnit = profile.xUnit() # e.g. wavelength unit, e.g. nanometer
    print(yValues)
    #everything that is stored in the BLOB field ==
    # the BLOB data is stored in the field "values"

    blobDataDictionary = profile.values() #<- lazy BLOB decoding
    assert isinstance(blobDataDictionary, dict)






