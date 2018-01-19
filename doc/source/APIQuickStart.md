# Quick Start EnMAP-Box API

## Access the EnMAP-Box

### Start the EnMAP-Box from scratch

```
#!python

from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox.gui.utils import initQgisApplication

qgsApp = initQgisApplication()
enmapBox = EnMAPBox(None)
enmapBox.openExampleData(mapWindows=1)

qgsApp.exec_()
qgsApp.quit()
```

### Close the EnMAP-Box


```
#!python

enmapBox = EnMAPBox.instance()
enmapBox.close()

```

### Use an existing EnMAP-Box instance

The EnMAPBox object is designed as singleton, i.e. only one EnMAPBox instance can exist per thread.

```
#!python

from enmapbox.gui.enmapboxgui import EnMAPBox
enmapBox = EnMAPBox.instance()

```


## Data sources

### Add a new data source (raster/vector/any other file)


```
#!python

enmapBox = EnMAPBox.instance()
enmapBox.addSource('filepath')
```

### Get the data sources which are listed in the EnMAP-Box

```
#!python

enmapBox = EnMAPBox.instance()

# print all sources
for source in enmapBox.dataSources():
    print(source)

# print raster sources only
for source in enmapBox.dataSources('RASTER'):
    print(source)


```

### Remove a data source


```
#!python

enmapBox = EnMAPBox.instance()
enmapBox.removeSource('path_to_source')

```


## Add new windows to view data

```
#!python

enmapBox = EnMAP-Box.instance()
enmapBox.createDock('MAP')  # a spatial map
enmapBox.createDock('SPECLIB') # a spectral library
enmapBox.createDock('TEXT') # a text editor
enmapBox.createDock('WEBVIEW') # a browser
enmapBox.createDock('MIME') # a window to drop mime data

```