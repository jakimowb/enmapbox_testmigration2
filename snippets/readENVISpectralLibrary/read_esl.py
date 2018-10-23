from enmapboxtestdata import speclib as pathSpecLib
from enmapbox.gui.speclib.spectrallibraries import SpectralLibrary
SpecLIB = SpectralLibrary.readFrom(pathSpecLib)
p0 = SpecLIB[0]
p0.plot()
SpecLIB.plot()

