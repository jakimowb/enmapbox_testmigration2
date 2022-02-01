.. include:: /icon_links.rst

.. _spectral_libraries:

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

You can add a new **Spectral Library Window** using the *Add Spectral Library Window* |viewlist_spectrumdock| button in the toolbar or from the menu bar
:menuselection:`View --> Add Spectral Library Window`.

A new view appears where you can start to collect spectra or import an existing library by using the *Import Spectral Library* |speclib_add| button.

* Import of different formats is possible, e.g. ENVI Spectral Library, Geopackage, ASD Field Spectrometer measurements, Raster Layer.


.. figure:: /img/SpecLib_overview.png
   :width: 100%

   Overview of the Spectral Library Window with several collected and labeled spectra and main tools

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
   * - |mActionAddLegend|
     - Activate to change spectra representation
   * - |speclib_usevectorrenderer|
     - Activate to use colors from map vector symbology
   * - |system|
     - Enter the Spectral Library Layer Properties
   * - |mActionToggleEditing|
     - Toggle editing mode
   * - |mActionMultiEdit|
     - Toggle multi editing mode
   * - |mActionSaveAllEdits|
     - Save edits
   * - |mActionRefresh|
     - Reload the table
   * - |mActionNewTableRow|
     - Add feature
   * - |mActionDeleteSelected|
     - Delete selected features
   * - |mActionEditCut|
     - Cut selected rows to clipboard
   * - |mActionEditCopy|
     - Copy selected rows to clipboard
   * - |mActionEditPaste|
     - Paste features from clipboard
   * - |mIconExpressionSelect|
     - Select by Expression
   * - |mActionSelectAll|
     - Selects all elements in
       the spectral library
   * - |mActionInvertSelection|
     - Inverts the current selection
   * - |mActionDeselectAll|
     - Remove selection (deselect everything)
   * - |mActionSelectedToTop|
     - Move selection to the top
   * - |mActionFilter2|
     - Select / filter features using form
   * - |mActionPanToSelected|
     - Pan map to selected rows
   * - |mActionZoomToSelected|
     - Zoom map to selected rows
   * - |mActionNewAttribute|
     - Add New field
   * - |mActionDeleteAttribute|
     - Delete field
   * - |mActionConditionalFormatting|
     - Conditional formatting
   * - |mAction|
     - Actions
   * - |mActionFormView|
     - Switch to form view
   * - |mActionOpenTable|
     - Switch to table view

**Collecting spectra:**

* Make sure to enable the |profile| button in the menu bar and open a raster from which you want to collect spectra in a new *Map Window*.
* Click on a desired location in the *Map Window*. The pixels spectral profile at this location will now be shown in
  the plot in the *Library Window*. Mind that this will only visualize the spectrum, but nothing is saved at this point.
* To add/save a selected spectrum to the library, click the |plus_green| button: A new table entry on the right of the window is added.
* If spectra should be added automatically to the library while a pixel is selected or clicked, enable the |profile_add_auto| button.

.. tip::

   Have a look at the :ref:`Spectral Profile Sources <spectral_profile_sources>` window for more advanced settings
   collecting spectra.

**Changing the units**

* You can change the unit of the axis by right-clicking into the spectral library and navigating to the respective option.

.. figure:: /img/SpectralLib_Units.png
   :width: 100%

   Spectral Library Window showing how to change the unit of the x-axis

* You can also change the units in the *Visualization View* in the **X Axis** field (see picture above)


**Add information to the attribute table:**

* Add additional fields to the table, e.g. in order to add information to every spectrum (id, name, classification label, ...).
* To do so, enable the *Editing mode* by activating  |mActionToggleEditing|.
* Now you can use the |mActionNewAttribute| button to add a new field (mind the type!).

  .. figure:: /img/speclib_add_field.png

     Example: Add a new text field (maximum 100 characters)


* After the new column is added, you can add information by double-clicking it.
* To delete a column, use the *Delete field button* |mActionDeleteAttribute|


**Selecting spectra and showing coordinates**

* Locations of spectra (if available) can be visualized as a point layer by right-clicking into a map window, and selecting :guilabel:`Add Spectral Library`

  .. figure:: /img/AddCoordinates_Speclib.png
     :width: 100%

     Add point coordinates to image

* Spectra can be selected in the attribute table and in the plot window itself. Selected spectra will be highlighted (blue background
  in the table; thicker line in a different color in the plot window).
* Hold the :kbd:`Shift` key to select multiple spectra.
* A selection can be removed by clicking the |mActionDeselectAll| button.

  .. figure:: /img/SelectSpectra.png
     :width: 100%

     Selection of spectra in the Spectral Library Window

* Spectra can be removed by using the |mActionDeleteSelected| button.
* Save the collected spectra with the *Save Profiles in Spectral Library* |speclib_save| button.

.. tip:: You can inspect an individual value of a spectrum by holding the :kbd:`Alt` key and clicking some position along the spectrum

You can also select and filter spectra with the common vector filter and selection tools.

  .. figure:: /img/FilterSpectra.png
     :width: 100%

**Colorize spectra by attribute:**

* In order to colorize your spectra according to their attributes, you have to categorize the points accordingly.
* In the *Data Views* section on the left, right click on the spectral library data that we are currently using and select the *Layer Properties*
* Switch to the |symbology| :guilabel:`Symbology` tab and select the :guilabel:`Categorized` renderer at the top
* In the :guilabel:`Column` droplist select the desired column and click :guilabel:`Classify`
* Confirm with :guilabel:`Ok` and close the window.

  ..  figure:: /img/PropertiesSpecLib.png
      :width: 100%

* In the Spectral Library Window activate the visualization settings with the |mActionAddLegend| button.
* Right-click on **Color** and select *Use vector symbol colors* |speclib_usevectorrenderer|.

  ..  figure:: /img/ColorizeSpectra.png
      :width: 100%


.. _spectral_profile_sources:


Spectral Profile Sources
~~~~~~~~~~

This menu manages the connection between raster sources and spectral library windows.

  .. figure:: /img/SpectralProfileSources.png
     :width: 80%

**Buttons of the Spectral Library Window**

.. csv-table::
   :header-rows: 1
   :widths: auto

   Button, Description
   |plus_green|,  add a new profile source entry
   |cross_red|, remove selected entries

**Profiles**
 * This section is used to define the input data from where to take the spectral information from.
 * You can also select or define a color for the spectra and choose between two different sampling methods.

*Source*
 * Here you can specify a source raster dataset
 * Double-clicking in the cell will open up a dropdown menu where you can select from all loaded raster datasets.

*Sampling*
 * Select *Single Profile* or *Kernel* by double-clicking into the cell

*Scaling*
 * Choose how spectra are sampled.
 * Define the scaling factors by setting the *Offset* and *Scale* value.

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


If you want to only collect spectra for one class, e.g. cropland, define the class in the Spectral Profile Source under **name**.
If you now click into the image, the spectra is automatically added and named as cropland.

  .. figure:: /img/SpectralProfileSourcesDemo.png
     :width: 100%

     Example: How to use the Spectral Profile Sources Panel

* Calculate different spectral profiles *

* You can calculate new spectral profiles, e.g. a 5x5 mean in the **Spectral Profile Sources** window.
* Add a new column in the attribute table with a meaningful name and select **Type** *Spectral Profile*
* In the Spectral Profile Sources window navigate to the newly created attribute, select the **Source** and switch from *Single Profile* to *Kernel*.
* Choose the **Kernel** you want to use and the **Aggregation** method.

   .. figure:: /img/CalculateSpectra.png
      :width: 100%

      Example: Calculating spectral profiles

* You can now collect spectra in the image and visualize the profiles in different colors using the visualization settings.
* Change the color of the different profiles (see also section **Colorize spectra by attribute**).

   .. figure:: /img/CalculateSpectraVisualization.png
      :width: 100%

       Example: How to colorize spectra according to their attribute

Spectral Library Formats
~~~~~~~~~~

The EnMAP-Box supports several external spectral library formats, e.g. the ENVI standard spectral library format (:file:`.sli` + :file:`.hdr`).

Click the |mIconCollapse| button next to |speclib_add| :sup:`Import spectral profiles` to open the import dialog:

  .. figure:: /img/speclib_import_dialog.png
     :width: 100%

   Import dialog in the spectral library window


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

    .. figure:: /img/speclib_csv_example.png
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

    .. figure:: /img/speclib_json_example.png
       :width: 100%



.. aufbau: .sli + .hdr + csv

.. hdr: (ENVI standard) wichtig wavelength information

.. csv header names referenzieren zu spectra names in hdr datei

.. zweite csv:
.. classification case: Klassenname; KLassenname (rgb tuple) ,basename.attributname.classdef.csv

.. regression case: klasse + farbtuple + nodata wert  , basename.attributname.regrdef.csv
