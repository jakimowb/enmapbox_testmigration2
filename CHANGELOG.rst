CHANGELOG
=========
Version 3.8
-----------
* rename layers, map views and spectral library views with F2
* model browser: improved visualization (#645, #646, #647), array values can be copied to clipboard (#520)
* layers can be moved between maps (#437)
* updated pyqtgraph to 0.12.1

Version 3.7
-----------

* added EnMAP L1B, L1C and L2A product reader
* added PRISMA L2D product import
* added DESIS L2A product reader
* added Classification Statistics PA
* added Save As ENVI Raster PA: saves a raster in ENVI format and takes care of proper metadata storage inside ENVI header file
* added Aggregate Raster Bands PA: allows to aggregate multiband raster into a single band using aggregation functions like min, max, mean, any, all, etc.
* classification scheme is now defined by the layer renderer
* [Spectral Resampling PA] reworked spectral resampling
* [Classification Workflow] support libraries as input
* [ImageMath] added predefined code snippets
* [Subset Raster Wavebands PA] support band selection via wavelength
* LayerTreeView: enhanced context menus:
  double click on map layer opens Properties Dialog,
  double click on a vector layers' legend item opens a Symbol dialog
* GDAL raster metadata can be modified (resolves #181)
* map canvas preserves scale on window resize (#409)
* Reclassify Tool: can save and reload the class mapping, fixed (#501)
* several fixed in Image Cube App
* updated PyQtGraph to version 0.11
* Virtual Raster Builder and Image Cube can select spatial extents from other QGIS / EnMAP-Box maps
* several improvements to SpectralLibrary, e.g. to edit SpectralProfile values
* QGIS expression builder:
    added 'format_py' to create strings with python-string-format syntax,
    added spectralData() to access SpectralProfile values
    added spectralMath(...) to modify  / create new SpectralProfiles
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
* updated EnPTEnMAPBoxApp (see https://git-pages.gfz-potsdam.de/EnMAP/GFZ_Tools_EnMAP_BOX/enpt_enmapboxapp for documentation)
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

