![EnMAP-Box Logo](http://www.enmap.org/sites/default/files/pictures/logos/logo-enmap-box-thumb.jpg)

# README #

The EnMAP-Box software is developed to be used as a QGIS plugin. The installation steps include: 

1. Install QGIS
2. Clone the EnMAP-Box Repository
3. Activate the EnMAP-Box Plugin inside QGIS

> Steps 2 and 3 will later be replaced by an installation via the QGIS Plugins Manager.

If you have any questions feel free contacting us: 
[Andreas Rabe](https://www.geographie.hu-berlin.de/de/Members/rabe_andreas),
[Benjamin Jakimow](https://www.geographie.hu-berlin.de/de/Members/jakimow_benjamin) and
[Sebastian van der Linden](https://www.geographie.hu-berlin.de/de/Members/linden_sebastian)

## 1. Install QGIS ##

Download the newest [QGIS release](http://www.qgis.org/en/site/forusers/download.html) and install it.

## 2. Clone the EnMAP-Box Repository ##

### via command line ###

If you are familiar to Git and Git LFS use: 

`git lfs clone https://bitbucket.org/hu-geomatics/enmap-box.git`

### via SourceTree GUI Client ###

If you have no expirience with Git Repositories, we recommend to use
[SourceTree](https://www.sourcetreeapp.com/). 
This graphical Git client is nicely integrated within Bitbucket and allows a 
seamless installation of the EnMAP-Box without command line interactions.

> Note that the following intructions are examplified on a Windows system. Dialogs my appear in a slightly different look on MacOS or Linux systems. 

Download and install [SourceTree](https://www.sourcetreeapp.com/). 
If asked, agree to the **Upgrade Git LFS** and **Upgrade Git LFS Bitbucket Adapter** dialogs.

Now we can use SoureTree to clone the EnMAP-Box repository. Select `File -> Clone / New`

![open in source tree](README/cloneInSourceTree.png)

- set **Source Path / URL** to the EnMAP-Box repository: `https://bitbucket.org/hu-geomatics/enmap-box.git`

- select a **Destination Path**, e.g. `C:\QGISPlugins\enmap-box`

- press **Clone**

If asked, aggree to the **Run 'git lfs pull' now** dialog

## 3. Activate the EnMAP-Box Plugin inside QGIS ###

### set QGIS_PLUGINPATH ###

Inside QGIS we can now mark the EnMAP-Box Repository as a QGIS Plugin. From the QGIS menu select `Settings -> Options...`, select the **System** tab on the sidebar and navigate down to the **Environment** section.  

![Options | System](README/optionsSystem.png)

- if not already existing, use the `+` button to create a new environment variable

- set the *Apply* field to `Prepend`

- set the *Value* field to the EnMAP-Box Repository parent folder (e.g. `C:\QGISPlugins`)

- press **Ok** close the dialog

- restart QGIS

### activate the EnMAP-Box inside the QGIS Plugins Manager

The EnMAP-Box is now known to QGIS but needs to be activated inside the **QGIS Plugins Manager**. 
Therefor select `Plugins -> Manage and Install Plugins...`, select the **Installed** tab on the sidebar and make sure that the **EnMAP-Box 3** plugin is checked.

![plugins | installed](README/pluginsInstalled.png)

Also make sure that the **Processing** plugin is checked, which enables the *QGIS Processing Framework*, which is a prerequisite to the *EnMAP-Box AlgorithmProvider*.

![plugins | installed](README/pluginsInstalled2.png)

The **EnMAP-Box Multi-Frame Viewer** icon
![plugins | installed](README/boxIcon.png)
should now be visible inside the **QGIS Plugins Toolbar**.

### activate the EnMAP-Box AlgorithmProvider ###

The **EnMAP-Box AlgorithmProvider** might be deactived by default inside the **QGIS Processing Framework**. If so, from the QGIS menu select `Processing -> Options...`, navigate to **Providers -> EnMAP-Box** and check the **Activate** checkbox.

![plugins | installed](README/processingOptions.png)

The **EnMAP-Box AlgorithmProvider** should now be visible inside the **QGIS Processing Toolbox**:

![plugins | installed](README/algorithmProvider.png)

# Have Fun :-) #