![EnMAP-Box Logo](http://www.enmap.org/sites/default/files/pictures/logos/logo-enmap-box-thumb.jpg)

# README

The EnMAP-Box software is developed to be used as a [QGIS plugin](http://docs.qgis.org/2.14/en/docs/user_manual/plugins/plugins.html "Learn more about QGOS Plugins"). The installation steps include: 

1. Install QGIS
2. Install EnMAP-Box
3. Activate the EnMAP-Box Plugin inside QGIS

> Steps 2 and 3 will later be replaced by an installation via the QGIS Plugins Manager.

If you have any questions feel free contacting us: 
[Andreas Rabe](https://www.geographie.hu-berlin.de/de/Members/rabe_andreas),
[Benjamin Jakimow](https://www.geographie.hu-berlin.de/de/Members/jakimow_benjamin) and
[Sebastian van der Linden](https://www.geographie.hu-berlin.de/de/Members/linden_sebastian)

## 1. Install QGIS

Download the newest [QGIS release](http://www.qgis.org/en/site/forusers/download.html) and install it.

> On Windows, we recommend using the *QGIS Standalone Installer*, instead of the *OSGeo4W Network Installer*. 
In the latter case you might have to install [Matplotlib](http://matplotlib.org/) manually.

## 2. Install EnMAP-Box

Download the newest [EnMAP-Box release](https://bitbucket.org/hu-geomatics/enmap-box/downloads/).

Extract the `v*.zip/enmap-box` folder into the `~/.qgis/python/plugins` folder in your [home directory](https://en.wikipedia.org/wiki/Home_directory "Find out where your home directory is located.").
(e.g. `C:\Users\USERNAME\.qgis2\python\plugins\enmap-box`)

> Advanced user might also install the EnMAP-Box by
[cloning this repository](README/CloneTheRepository.md) into the `~/.qgis/python/plugins` folder. 
The current release is the HEAD commit of the *master* branch. 

## 3. Install external Dependencies

Successfully installing dependencies in a *QGIS-Python* environment can be challenging.
Therefore we ship all *pure Python* dependencies together with the EnMAP-Box.

Unfortunately, the following dependencies must be install from a source distribution: 

- [scikit-learn](http://scikit-learn.org/stable/)

Please find a system specific installation description here:
[Windows](README/installDependenciesOnWindows.md),
[MacOS](README/installDependenciesOnMacOS.md)

## 4. Activate the EnMAP-Box inside QGIS

Open the **Plugins | Installed** dialog `Plugins -> Manage and Install Plugins...` 
and activate the **EnMAP-Box 3** plugin.

![plugins | installed](README/pluginsInstalled.png)

Also make sure that the **Processing** plugin is checked, which enables the *QGIS Processing Framework*.

![plugins | installed](README/pluginsInstalled2.png)

The **EnMAP-Box Viewer**
![plugins | installed](README/boxIcon.png)
should now be visible inside the **QGIS Plugins Toolbar** and 
the **EnMAP-Box AlgorithmProvider** be visible inside the **QGIS Processing Toolbox**:

![plugins | installed](README/algorithmProvider.png)

If The **EnMAP-Box AlgorithmProvider** might be deactived by default inside the **QGIS Processing Framework**. If so, from the QGIS menu select `Processing -> Options...`, navigate to **Providers -> EnMAP-Box** and check the **Activate** checkbox.

![plugins | installed](README/processingOptions.png)

# Have Fun :-) #