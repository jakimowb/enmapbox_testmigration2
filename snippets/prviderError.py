
isinstance(c, QgsProcessingAlgorithm)
reg =  QgsApplication.processingRegistry()
provider = reg.providerById('enmapbox')
assert isinstance(provider, QgsProcessingProvider)

from processing.algs.gdal.buildvrt import buildvrt
provider.addAlgorithm(buildvrt())

from enmapboxgeoalgorithms.algorithms import ALGORITHMS, ClassDefinitionFromRaster

#Ok
c = ClassDefinitionFromRaster()
print(c.name())

#Error
c = ALGORITHMS[0]
print(c.name())

provider.addAlgorithm(c)

#refresh
import processing.core.ProcessingConfig
processing.core.ProcessingConfig.settingsWatcher.settingsChanged.emit()





2018-04-20T14:27:43	CRITICAL	Failed to load EnMAPBoxGeoAlgorithms.
			wrapped C/C++ object of type ClassDefinitionFromRaster has been deleted
			PYTHONPATH:
			C:/PROGRA~1/QGIS3~1.0/apps/qgis/./python
			C:/PROGRA~1/QGIS3~1.0/apps/qgis/./python/plugins
			C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python
			C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python
			C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins
			C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\enmapboxplugin
			C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\timeseriesviewerplugin
			C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\vrtbuilderplugin
			C:\PROGRA~1\QGIS3~1.0\apps\Python36
			C:\PROGRA~1\QGIS3~1.0\apps\Python36\DLLs
			C:\PROGRA~1\QGIS3~1.0\apps\Python36\lib
			C:\PROGRA~1\QGIS3~1.0\apps\Python36\lib\site-packages
			C:\Program Files\QGIS 3.0\bin
			C:\Program Files\QGIS 3.0\bin\python36.zip
			C:\Users\geo_beja\AppData\Roaming\Python\Python36\site-packages
			C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\enmapbox
			C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\site-packages
			C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\timeseriesviewerplugin\site-packages
			C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\timeseriesviewerplugin\timeseriesviewer
			C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\vrtbuilderplugin\vrtbuilder


C:/PROGRA~1/QGIS3~1.0/apps/qgis/./python
C:/PROGRA~1/QGIS3~1.0/apps/qgis/./python/plugins
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\enmapboxplugin
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\enmapboxplugin\enmapbox\apps
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\enmapboxplugin\enmapbox\coreapps
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\timeseriesviewerplugin
C:/Users/geo_beja/AppData/Roaming/QGIS/QGIS3\profiles\default/python/plugins\vrtbuilderplugin
C:\PROGRA~1\QGIS3~1.0\apps\Python36
C:\PROGRA~1\QGIS3~1.0\apps\Python36\DLLs
C:\PROGRA~1\QGIS3~1.0\apps\Python36\lib
C:\PROGRA~1\QGIS3~1.0\apps\Python36\lib\site-packages
C:\Program Files\QGIS 3.0\bin
C:\Program Files\QGIS 3.0\bin\python36.zip
C:\Users\geo_beja\AppData\Roaming\Python\Python36\site-packages
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\enmapbox
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\enmapbox\apps
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\enmapbox\coreapps
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\site-packages
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\site-packages\hubdc\calculator
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\enmapboxplugin\site-packages\vrtbuilder
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\timeseriesviewerplugin\site-packages
C:\Users\geo_beja\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\timeseriesviewerplugin\timeseriesviewer