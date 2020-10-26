CHANGELOG
=========
Version 3.7
-----------

* LayerTreeView: enhanced context menus,
  double click on map layer opens Properties Dialog,
  double click on a vector layers' legend item opens a Symbol dialog
* GDAL raster metadata can be modified (resolves #181)
* map canvas preserves scale on window resize (#409)
* Reclassify Tool: can save and reload the class mapping, fixed (#501)
* several improvements to SpectralLibrary, e.g. to edit SpectralProfile values
* adds 'format_py' to QgsExpressionWidget to format string like in python
* fixes some bugs in imageCube app



Version 3.6
-----------
(including hotfixes from 2020-06-22)

* added workaround for failed module imports, e.g. numba on windows (#405)
* EnMAP-Box plugin can be installed and started without having none-standard python packages installed (#366)
* Added installer to install missing python packages (#371)
* Map Canvas Crosshair can now show the pixel boundaries of any raster source known to QGIS
* Spectral Profile Source panel
    * is properly updated on removal/adding of raster sources or spectral libraries
    * allows to define source-specific profile plot styles (#422, #468)
* Spectral Library Viewer
    * added color schemes to set plot and profile styles
    * fixed color scheme issue (# fixed #467 )
    * profile styles can be changed per profile (#268)
    * current/temporary profiles are shown in the attribute table
    * added workaround for #345 (Spectral library create new field: problems with default fields)
    * loading profiles based in vector position is done in a background process (closed #329)
    * profile data point can be selected to show point specific information, e.g. the band number (#462, #267)
    * closed #252
* SpectralLibrary
    * implemented SpectralProfileRenderer to maintain profile-specific plot styles
* Classification Scheme Widget allows to paste/copy classification schemes from/to the clipboard.
  This can be used to copy classes from other raster or vector layers, or to set the layer renderer
  according to the classification scheme
* updated in LMU vegetation app
* updated EnPTEnMAPBoxApp (see http://enmap.gitext.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp for documentation)
* added EnSoMAP and EnGeoMAP applications provided by GFZ
* added ONNS application provided by HZG
* removed several bugs, e.g. #285, #206,

Version 3.5
-----------

(including last hotfixes from 2019-11-12)

* removed numba imports from LMU vegetation app
* vector layer styling is loaded by default
* fixed error that was thrown when closing the EnMAP-Box
* fixed bug in SynthMixApplication
* Spectral Library Viewer: import and export of ASD, EcoSIS and SPECCHIO csv/binary files
* Spectral Profile Source panel: controls how to extract SpectralProfiles and where to show them
* supports import of multi-dimensional raster formats, like HDF and netCDF
* ImageCube viewer to visualize hyperspectral data cubes (requires opengl)
* Added CONTRIBUTORS.md and "How to contribute" section to online documention
* Documentation uses HYPERedu stylesheet (https://eo-college.org/members/hyperedu/)
* fixed start up of EO Time Series Viewer and Virtual Raster Builder QGIS Plugins from EnMAP-Box

Version 3.4
-------------------------------------------

* Spectral Library Viewer: import spectral profiles from raster file based on vector positions
* Classification Widgets: copy / paste single class informations
* Map tools to select / add vector features
* fixed critical bug in IVVRM
* several bug fixed and minor improvements

Version 3.3
-------------------------------------------

* added user +  developer example to RTF documentation
* renamed plugin folder to "EnMAP-Box"
* SpectralLibraries can be renamed and added to
  map canvases to show profile locations
* SpectraProfiles now styled like point layers:
  point color will be line color in profile plot
* Workaround for macOS bug that started
  new QGIS instances again and again and ...
* Classification Workflow App
* Re-designed Metadata Editor
* Several bug fixes

Version 3.2
-------------------------------------------

* ...

Version 3.1
-------------------------------------------

* EnMAP-Box is now based on QGIS 3, Qt 5.9,Python 3 and GDAL 2.2
* QGISP lugin Installation from ZIP File
* readthedocs documentation
  https://enmap-box.readthedocs.io/en/latest/index.html

previous versions
-------------------------------------------

* version scheme following build dates

