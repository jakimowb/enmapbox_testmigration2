.. _Classification dataset (from table with categories and feature fields):

**********************************************************************
Classification dataset (from table with categories and feature fields)
**********************************************************************

Store attribute table data into a pickle file.


**Parameters**


:guilabel:`Table` [vector]
    Table with feature data X and target data y.


:guilabel:`Fields with features` [field]
    Fields used as features. Values may be given as strings, but must be castable to float.


:guilabel:`Field with class values` [field]
    Field used as class value.


:guilabel:`Field with class names` [field]
    Field used as class name. If not specified, class values are used as class names.


:guilabel:`Field with class colors` [field]
    Field used as class color. Values may be given as hex-colors, rgb-colors or int-colors.

**Outputs**


:guilabel:`Output dataset` [fileDestination]
    Output destination pickle file.

