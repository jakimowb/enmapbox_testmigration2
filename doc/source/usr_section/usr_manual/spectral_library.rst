.. include:: /icon_links.rst

Spectral Libraries
==================
A *Spectral Library* is a collection of profiles with arbitrary profile-wise data and metadata,
stored as pickled dictionaries inside (multiple) binary fields. Dictionary items are:

  * x: list of x values (e.g. wavelength)
  * y: list of y values (e.g. surface reflectance)
  * xUnit: x value units (e.g. nanometers)
  * yUnit: y value units (e.g. ???)
  * bbl: the bad bands list


Spectral Library Window |viewlist_spectrumdock|
~~~~~~~~~~

The *Spectral Library Window* can be used to visualize, collect and label spectra. It directly interacts with the Map Window(s), which
means spectra can be directly collected from an image. Furthermore, external libraries (ENVI Spectral Library) can be imported.

* Add a new **Spectral Library Window** using the |viewlist_spectrumdock| :sup:`Add Spectral Library Window` button in the toolbar or from the menu bar
  :menuselection:`View --> Add Spectral Library Window`

* You can import and open existing libraries using the |speclib_add| :sup:`Import Spectral Library` button

.. figure:: C:/Users/PC/Desktop/EnMap/SpectralLibrary.png
   :width: 100%

   Spectral Library Window with several collected and labeled spectra


**Buttons of the Spectral Library Window:**

.. list-table::
   :widths: auto
   :header-rows: 1

   * - Button
     - Description
   * - |plus_green|
     - Adds currently overlaid profiles
       to the spectral library
   * - |profile_add_auto|
     - Activate to add profiles automatically
       into the spectral library
   * - |speclib_add|
     - Import Spectral Library
   * - |speclib_save|
     - Save Spectral Library
   * - |mActionSelectAll|
     - Selects all elements in
       the spectral library
   * - |mActionInvertSelection|
     - Inverts the current selection
   * - |mActionDeselectAll|
     - Remove selection (deselect everything)
   * - |mActionRefresh|
     - Reload the table
   * - |mActionToggleEditing|
     - Toggle editing mode
   * - |mActionEditCut|
     - Cut selected rows to clipboard
   * - |mActionEditCopy|
     - Copy selected rows to clipboard
   * - |mActionEditPaste|
     - Paste features from clipboard
   * - |mActionDeleteSelected|
     - Delete selected features
   * - |mActionSaveAllEdits|
     - Save edits
   * - |mActionNewAttribute|
     - Add New field
   * - |mActionDeleteAttribute|
     - Delete field
   * - |system|
     - Enter the Spectral Library Layer Properties
   * - |mActionFormView|
     - Switch to form view
   * - |mActionOpenTable|
     - Switch to table view
   * - |mActionPanToSelected|
     - Pan map to selected rows
   * - |mActionFilter2|
     - Select / filter features using form
   * - |mActionZoomToSelected|
     - Zoom map to selected rows
   * - |mActionConditionalFormatting|
     - Conditional formatting
   * - |speclib_usevectorrenderer|
     - Activate to use colors from map vector symbology
   * - |mActionSelectedToTop|
     - Move selection to the top

**Collecting spectra:**

* Make sure to enable the |profile| button in the menu bar and open a raster from which you want to collect spectra in a new *Map Window*.
* Click on a desired location in the *Map Window*. The pixels spectral profile at this location will now be shown in
  the plot in the *Library Window*. Mind that this will only visualize the spectrum, but nothing is saved at this point.
* To add/save a selected spectrum to the library, click the |plus_green| button: A new table entry on the right of the window is added.
* If spectra should be added automatically to the library while a pixel is selected or clicked, enable the |profile_add_auto| button.


.. tip::

   Have a look at the :ref:`Spectral Profile Sources <spectral_profile_sources>` window for more advanced settings
   collecting spectra.


**Add information to the attribute table:**

* You can add additional fields to the table, e.g. in order to add information to every spectrum (id, name, classification label, ...).
* To do so, enable the *Editing mode* by activating  |mActionToggleEditing|.
* Now you can use the |mActionNewAttribute| button to add a new field (mind the type!).

  .. figure:: ../../img/speclib_add_field.png

     Example: Add a new text field (maximum 100 characters)


* After the new column is added, you can add information by double-clicking it.
* To delete a column, use the *Delete field button* |mActionDeleteAttribute|


**Selecting spectra and showing coordinates**

* Locations of spectra (if available) can be visualized as a point layer by right-clicking into a map window, and selecting :guilabel:`Add Spectral Library`

  .. figure:: ../../img/AddCoordinates_Speclib.png

     Add point coordinates to image

* Spectra can be selected in the table and in the plot window itself. Selected spectra will be highlighted (blue background
  in the table; thicker line in a different color in the plot window).
* Hold the :kbd:`Shift` key to select multiple spectra.
* A selection can be removed by clicking the |mActionDeselectAll| button.

  .. figure:: ../../img/SelectionSpectra.png

     Selection of spectra in the Spectral Library Window

* Spectra can be removed by using the |mActionDeleteSelected| button.
* Save the collected spectra with the *Save Profiles in spectral library* |speclib_save| button.

**Colorize spectra by attribute:**

* Open the *Spectral Library Properties* using the |system| button on the lower right.
* Switch to the |symbology| :guilabel:`Symbology` tab and select the :guilabel:`Categorized` renderer at the top
* In the :guilabel:`Column` droplist select the desired column and click :guilabel:`Classify`

  .. image:: ../../img/speclib_properties.png

* Confirm with :guilabel:`Apply` and close the window.
* In the *Spectral Library Window*, activate |speclib_usevectorrenderer|  to use the previously given colors.


.. _spectral_profile_sources:


Spectral Profile Sources
~~~~~~~~~~

This menu manages the connection between raster sources and spectral library windows.

  .. image:: ../../img/SpectralProfileSources.png

**Buttons of the Spectral Library Window**

.. csv-table::
   :header-rows: 1
   :widths: auto

   Button, Description
   |plus_green|,  add a new profile source entry
   |cross_red|, remove selected entries

**Source**
 * Here you can specify a source raster dataset
 * Double-clicking in the cell will open up a dropdown menu where you can select from all loaded raster datasets.

**Sampling**
 * Choose how spectra are sampled.
 * Double-click into the cell to open the dropdown menu, where you have several options available:

.. csv-table::
   :header-rows: 1
   :widths: auto

   Option, Description
   SingleProfile, Extracts the spectral signature of the pixel at the selected location
   Sample3x3, Extracts spectral signatures of the pixel at the selected location and its adjacent pixels in a 3x3 neighborhood.
   Sample5x5, Extracts spectral signatures of the pixel at the selected location and its adjacent pixels in a 5x5 neighborhood.
   Sample3x3Mean, Extracts the mean spectral signature of the pixel at the selected location and its adjacent pixels in a 3x3 neighborhood.
   Sample5x5Mean, Extracts the mean spectral signature of the pixel at the selected location and its adjacent pixels in a 5x5 neighborhood.

**Destination**
 * Select into which spectral library should the extracted spectra be imported.
 * Double-click to open the dropdown menu.

**Scale**
 * Scale factor for on-the-fly conversion.
 * E.g. if your raster is scaled between 0-10000 but you want to store values between 0 and 1 in the spectral library

  .. figure:: ../../img/SpectralProfileSourcesDemo.png

     Example: How to use the *Spectral Profile Sources Panel*


Spectral Library Formats
~~~~~~~~~~
The EnMAP-Box supports the ENVI standard spectral library format (.sli + .hdr file). Spectral libraries can be imported
as single line raster using the processing algorithm :menuselection:`Auxillary --> Import Library`.

.. todo:: Support for further formats will be implemented soon (e.g. import spectral library from ASD field spectrometer)

.. screenshot von der tetslibrary im speclib viewer

.. Auxillary -> Import Library


Labelled Spectral Library
~~~~~~~~~~

The labelled spectral library extents the default .sli format by adding additional metadata information (e.g., class labels, class colors).
This information is stored by adding a .csv and .json file to the default spectral library, so that the labelled spectral library consists of

* .sli file (ENVI standard)
* .hdr file (ENVI standard)
* .csv file (containing the additional information)

  * should be comma-separated csv
  * should have same basename as .sli file
  * first row stores the headers, where the first element has to be the spectra names as specified in the .hdr file:

    .. code-block:: csv

       spectra names, attribute1, attribute2

  * Example from the EnMAP-Box test dataset:

    .. figure:: ../../img/speclib_csv_example.png
       :width: 100%

* .json file (stores class name and class color information)

  * should have same basename as .sli file
  * class name and color information should be provided for every attribute in the csv:

    .. code-block:: json

      {
        "attribute_name": {
          "categories":  [
            [0, "unclassified", [0, 0, 0]],
            [1, "class1", [230, 0, 0]],
            [2, "class2", [56, 168, 0]],
            [3, "class3", [168, 112, 0]],
            [4, "class4", [0,100,255]]
          ],
          "no data value": 0,
          "description": "Classification"
      }

  * The keys ``categories``, ``no data value`` and ``description`` should not be altered. But change ``attribute_name`` according to your data.
  * ``no data value`` should be supplied
  * Example from the EnMAP-Box test dataset:

    .. figure:: ../../img/speclib_json_example.png
       :width: 100%



.. aufbau: .sli + .hdr + csv

.. hdr: (ENVI standard) wichtig wavelength information

.. csv header names referenzieren zu spectra names in hdr datei

.. zweite csv:
.. classification case: Klassenname; KLassenname (rgb tuple) ,basename.attributname.classdef.csv

.. regression case: klasse + farbtuple + nodata wert  , basename.attributname.regrdef.csv
