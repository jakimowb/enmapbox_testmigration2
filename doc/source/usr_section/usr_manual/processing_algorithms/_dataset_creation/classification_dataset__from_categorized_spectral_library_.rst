.. _Classification dataset (from categorized spectral library):

**********************************************************
Classification dataset (from categorized spectral library)
**********************************************************

Store spectral profiles that matches the given categories into a pickle file.
If the spectral library is not categorized, or the field with class values is selected manually, categories are derived from target data y. To be more precise: i) category values are derived from unique attribute values (after excluding no data or zero data values), ii) category names are set equal to the category values, and iii) category colors are picked randomly.

**Parameters**


:guilabel:`Categorized spectral library` [vector]
    Categorized spectral library with feature data X (i.e. spectral profiles) and target data y. It is assumed, but not enforced, that the spectral characteristics of all spectral profiles match. If not all spectral profiles share the same number of spectral bands, an error is raised.


:guilabel:`Field with class values` [field]
    Field with class values used as target data y. If not selected, the field defined by the renderer is used. If that is also not specified, an error is raised.


:guilabel:`Field with spectral profiles used as features` [field]
    Binary field with spectral profiles used as feature data X. If not selected, the default field is used. If that is also not specified, an error is raised.

**Outputs**


:guilabel:`Output dataset` [fileDestination]
    Output destination pickle file.

