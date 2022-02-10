# EnMAP-Box 3

![build status](https://img.shields.io/bitbucket/pipelines/hu-geomatics/enmap-box.svg)

![Logo](enmapbox/gui/ui/icons/enmapbox.svg)

The EnMAP-Box is free and open source [QGIS Plugin ](https://www.qgis.org) to visualize and process remote sensing raster data. 
It is particularly developed to handle imaging spectroscopy data, as from the upcoming EnMAP sensor.

![Screenshot](doc/source/img/screenshot_main3.png)

# Highlights:

* an easy-to-use graphical user interface for the visualization of vector and raster data sources in parallel and in spatially linked maps.

* collection and visualisation of spectral profiles spectral libraries. Spectral profiles can come from different sources, 
  e.g. raster images, field spectrometer or table-sheets.

* enhances the QGIS Processing Framework with many algorithms commonly used in
  remote sensing and imaging spectroscopy, e.g. support vector machines or random forest based raster classification, 
  regression, cluster approaches from the [scikit-learn](https://scikit-learn.org/stable/index.html) library.

* applications specific to imaging spectroscopy and the EnMAP program, e.g. a simulation of spectral profiles (IIVM), 
  atmospheric correction of EnMAP data, mapping of geological classes from EnMAP data and more...


Documentation: http://enmap-box.readthedocs.io

Git Repository: https://bitbucket.org/hu-geomatics/enmap-box

## How to clone

Use the following commands to clone the EnMAP-Box and update its submodules:

### TL;DR:

````bash
git clone --recurse-submodules git@bitbucket.org:hu-geomatics/enmap-box.git
cd enmapbox
git config --local include.path ../.gitconfig
````

### Detailed description

````bash
git clone git@bitbucket.org:hu-geomatics/enmap-box.git
````

After cloning, update the submodules which are hosted in other repositories
````bash
cd enmapbox
git submodule update --recursive
````

Of course, cloning and updating submodules can be done in one step
````bash

git clone --recurse-submodules git@bitbucket.org:hu-geomatics/enmap-box.git
````


At any time you can update the submodule with:

````bash
cd enmapbox
git submodule update --remote
````

Updating submodules automatically can be done by enabling:
````bash
git config --set submodule.recurse true
````

This setting (and maybe more in future) is also defined in the `.gitconfig`. 
You can add include it to your local repository by

````bash
git config --local include.path ../.gitconfig
````


Todo: push changes into submodule repository

````bash
cd <submodule>
git add .
git commit -m "my changes"
git push origin HEAD:master
````


## How to contribute

Our online documentation at [http://enmap-box.readthedocs.io](http://enmap-box.readthedocs.io/en/latest/general/contribute.html) describes how you can support the development of the EnMAP-Box.

## License

The EnMAP-Box is released under the GNU Public License (GPL) Version 3 or above. A copy of this licence can be found in 
the LICENSE.txt file that is part of the EnMAP-Box plugin folder and the EnMAP-Box repository, and also at
<http://www.gnu.org/licenses/>

Developing the EnMAP-Box under this license means that you can (if you want to) inspect and modify the source code and guarantees that you 
will always have access to an EnMAP-Box software that is free of cost and can be freely
modified.

## Dependencies

### QGIS Plugin Support: 

Repository: https://github.com/EnMAP-Box/qgispluginsupport

Included into EnMAP-Box code by git submodule. The following commands can be

1. To update QPS run: `git submodule update --remote`

2. You can automatically update submodules, for example when calling git pull, by:
   `git config --set submodule.recurse true`

3. This is already defined in the repositories `.gitconfig`. You can add include it to your local repository by
   `git config --local include.path ../.gitconfig`


## Support
You can get support in the following ways:

 -  Read the EnMAP-Box documentation [http://enmap-box.readthedocs.io](http://enmap-box.readthedocs.io)

 -  Open an issue with your question, bug report, feature request or other enhancement https://bitbucket.org/hu-geomatics/enmap-box/issues/new
 
 -  Write us an email: [enmapbox@enmap.org](mailto:enmapbox@enmap.org)



