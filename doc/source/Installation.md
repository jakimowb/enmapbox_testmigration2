# Installation

## General Information #

The EnMAP-Box 3 is developed as QGIS plugin. This requires to have installed:

1. [a recent QGIS version (>= 2.18).](#markdown-header-1-install-qgis)
2. [some external python dependencies, in particular scikit-learn.](#markdown-header-2-install-dependencies)
3. [the EnMAP-Box QGIS Plugin.](#markdown-header-3-install-the-enmap-box-plugin)

To update the EnMAP-Box you just need to repeat step 3.

#1. Install QGIS

OS specific download and install instructions can be found on http://www.qgis.org/en/site/forusers/download.html.

### macOS
The official macOS binaries for QGIS are hosted on http://www.kyngchaos.com/software/qgis but use the standard macOS python and are sometimes
a bit outdated. We prefere to use [Homebrew](https://brew.sh) for maintaining the QGIS installation:

Installation steps:

* Open the macOS terminal
* Install Homebrew

```
#!bash

/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
```

* Install the [OSGeo4MAC QGIS](https://github.com/OSGeo/homebrew-osgeo4mac)
 
```
#!bash
        
brew untap dakcarto/osgeo4mac
brew tap osgeo/osgeo4mac
brew tap --repair
brew install qgis2
```

* open the macOS Finder and navigate to where homebrew installed has installed the QGIS.app, e.g. `/usr/local/Cellar/qgis2/2.18.11_1/`

* Create an alias of the QGIS.app and put in into your /Application folder


### Windows

QGIS for Windows uses the OSGeo4W installer.  
If not linked into the Windows Start menu, you can start it from the OSGeo4W command line interface. 


You can install QGIS without administration rights:

* Download the QGIS / OOSGeo4W Installer as described in http://www.qgis.org/en/site/forusers/alldownloads.html
* Open the windows cmd shell and call ``set __COMPAT_LAYER=RUNASINVOKER``
* now start the OSGeo4W Installer ``<SETUP>.exe``. The OSGeo4W Setup Program will now start:

    * Advanced Install >>next>>
    * Download Source: Install from Internet >>next>>
    * Root Install Directory: Default or specify >>next>>
    * Local Package Directory: Default or specify >>next>>
    * Internet Connection Default or specify >>next>>
    * Download Site >>next>>
    * Select Packages: (QGIS Desktop)...

* after installation: to update, remove or re-install packages just call ``set __COMPAT_LAYER=RUNASINVOKER`` before starting the OSGeo4W Setup (``OSGeo4W\bin\setup.bat``)

## 2. Install dependencies
[id2]:
Parts of the EnMAP-Box require python packages that might not be part of your QGIS Installation.
To check which of them are missing, you might use the following test script:

* in QGIS Desktop: Plugins >> Python Console
* in the Python Console: Show Editor
* Copy the following script into the Editor and run it to find missing external packages


```
#!python

#required packages that are not delivered with the EnMAP-Box
import qgis, PyQt4.QtCore
from osgeo import gdal, ogr, osr
import pip, setuptools
import numpy, scipy, matplotlib
import sklearn

def hasMinimumVersion(version, requiredVersion):
    version = [int(n) for n in version.split('.')]
    requiredVersion = [int(n) for n in requiredVersion.split('.')]

    for n1, n2 in zip(version, requiredVersion):
        if n1 < n2:
            return False
    return True

assert hasMinimumVersion(numpy.version.version, '1.10.0')
assert hasMinimumVersion(sklearn.__version__, '0.19.0')
assert sklearn.__version__ == '0.19.0'
print('All required packages available')
```

We recommend to use the same package manager which was used to install QGIS to install the missing python packages as well.


### Notes for windows users
With except of scikit-learn, all required (python and non-python) packages should be installable with the OSGeo4W package installer.

* qgis (desktop)
* msys (command line utilities)
* setuptools (Libs)
* python-numpy (Libs)
* python-scipy (Libs)
* python-test (Libs)
* python-pip (Libs)
* matplotlib (Libs)

![Bild1.png](https://bitbucket.org/repo/7bo7M8/images/1419849024-Bild1.png)

Scikit-learn can be installed with pip:

* From the QGIS Python Shell:
  

```
#!python

import pip
pip.main(['install','sklearn'])

```

* From the OSGeo4W Shell / any other shell from which you can call the python.exe that is used by your QGIS installation.
* call ``pip install -U scikit-learn`` (or ``python -m pip install -U scikit-learn`` in case of an error message).

![Bild2.png](https://bitbucket.org/repo/7bo7M8/images/4153420878-Bild2.png)


## 3. Install the EnMAP-Box Plugin

Visit our [download section](https://bitbucket.org/hu-geomatics/enmap-box/downloads/)
to find and download the latest EnMAP-Box development. The EnMAP-Box plugin can be placed (A) in the default QGIS Plugin folder or (B) in a user defined plugin folder (requires the setting of environmental variable)

### (A) QGIS Plugin folder:

* extract and copy the `enmapboxplugin` folder into the QGIS Plugin folder
* by default this is the `<HOME>\.qgis2/python\plugins\` folder, e.g. `C:\Users\<USERNAME>\.qgis2/python\plugins\` on windows-
* open QGIS Desktop and activate the plugin: Plugins >> Manage and Install Plugins...

### (B) User defined plugin folder:

* extract and copy the `enmapboxplugin` folder to the user defined plugin folder
* open QGIS Desktop: **Settings > Options > System > Environment ** and click ** use custom variables **
* add / Append *QGIS_PLUGINPATH* with *<any\other\folder*
* activate the plugin QGIS Desktop: Plugins >> Manage and Install Plugins...

![Bild4.png](https://bitbucket.org/repo/7bo7M8/images/2736817488-Bild4.png)

## FAQ / Troubleshooting

### Error dialog: Wrong value for parameter MSYS##

**Description:** the following error occurs when activating the EnMAP-Box AlgorithmProvider in windows

![Unbenannt.PNG](https://bitbucket.org/repo/7bo7M8/images/4131973787-Unbenannt.PNG)

**Solution:** install the *msys (command line utilities)* package with the OSGeo4W package installer.