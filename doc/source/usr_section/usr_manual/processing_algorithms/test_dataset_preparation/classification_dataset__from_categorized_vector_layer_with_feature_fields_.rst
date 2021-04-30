.. _Classification dataset (from categorized vector layer with feature fields):

**************************************************************************
Classification dataset (from categorized vector layer with feature fields)
**************************************************************************

Store attribute table rows that matches the given categories into a pickle file.
If the layer is not categorized, or the field with class values is selected manually, categories are derived from the target data y. To be more precise: i) category values are derived from unique attribute values (after excluding no data or zero data values), ii) category names are set equal to the category values, and iii) category colors are picked randomly.

**Parameters**


:guilabel:`Categorized vector layer` [vector]
    Categorized vector layer specifying feature data X and target data y.


:guilabel:`Fields with features` [field]
    Fields with values used as feature data X.


:guilabel:`Field with class values` [field]
    Field with class values used as target data y. If not selected, the field defined by the renderer is used. If that is also not specified, an error is raised.

**Outputs**


:guilabel:`Output dataset` [fileDestination]
    Output destination pickle file.

