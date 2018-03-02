# -*- coding: utf-8 -*-

"""
***************************************************************************

    ---------------------
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import re
from osgeo import gdal, ogr

class MDKeyAbstract(object):
    """
    A MDKey connects a gdal.MajorObject or ogr.MajorObject and a TreeNode.
    It does not story any DataSet-specific state variables, only general information on the Metadata Object itself.
    """

    def __init__(self, name, valueType=str, isImmutable=False, options=None):
        """
        :param name: Name of the Metadata Key
        :param valueType: the type a returned DataSet Value will have in Python, e.g. str, int, MyClass
        :param isImmutable: True, if this Metadata Value can not be changed by a user
        :param options: [list-of-options]
        """
        self.mName = name
        self.mType = valueType
        self.mIsImmutable = isImmutable
        self.mOptions = options

    def readValue(self, obj):
        """
        Reads a value from a gdal/ogr object `obj
        :param obj: gdal.MajorObject or ogr.MajorObject, e.g. gdal.DataSet or gdal.Band
        :return: None, if Metadata does not exist
        """
        raise NotImplementedError('Abstract class')


    def writeValue(self, obj, value):
        """
        Converts `value` into somethinf gdal/ogr can write to the gdal/ogr object `obj`.
        :param obj: gdal.MajorObject or ogr.MajorObject, e.g. gdal.Dataset
        :param value: The value to be written, might be of any type
        :return: None (= success) or Exception (= unable to write)
        """
        assert type(value) == self.mType
        raise NotImplementedError('Abstract class')

    def __hash__(self):
        return hash(self.mName)

    def __eq__(self, other):
        if isinstance(other, MDKeyDomainString):
            return self.mName == other.mName
        else:
            return False


class MDKeyDomainString(MDKeyAbstract):
    """
    A MDKey provides a between a gdal.MajorObject or ogr.MajorObject and a TreeNode.
    It does not story any state variables.
    """

    @staticmethod
    def fromString(domain, name, exampleValue):
        example = str(exampleValue)
        parts = re.split('[,{}]', exampleValue)
        isList = len(parts) > 1
        v = parts[0]
        t = str
        try:
            v = int(v)
            t = int
        except:
            try:
                v = float(v)
                t = float
            except:
                pass

        return MDKeyDomainString(domain, name, valueType=t)



    def __init__(self, domain, name, valueMin=None, valueMax=None,
                 isImmutable=False, options=None, **kwargs):
        super(MDKeyDomainString, self).__init__(name, **kwargs)
        self.mDomain = domain
        self.mMin = valueMin
        self.mMax = valueMax
        self.mIsImmutable = isImmutable
        self.mOptions = options

    def readValue(self, obj):
        """
        Reads a value from a gdal/ogr object `obj
        :param obj:
        :return:
        """
        assert isinstance(obj, gdal.MajorObject) or isinstance(obj, ogr.MajorObject)
        valueString = obj.GetMetadataItem(self.mName, domain=self.mDomain)
        return self.mType(valueString)


    def writeValue(self, obj, value):
        """
        Formats the value `value` into a fitting string and writes it to the gdal/ogr object `obj`
        :param obj: gdal.MajorObject or ogr.MajorObject
        :param value: value of any type
        :return: None (= success) or Exception (= unable to write)
        """
        assert isinstance(obj, gdal.MajorObject) or isinstance(obj, ogr.MajorObject)

        error = None
        strValue = self.value2str(value)
        try:
            obj.SetMetadataItem(self.mName, strValue, domain=self.mDomain)
        except Exception as ex:
            error = ex
        return error



class MDKeyDescription(MDKeyAbstract):
    def __init__(self, name='Description'):
        super(MDKeyDescription, self).__init__(name)

    def readValue(self, obj):
        assert isinstance(obj, gdal.MajorObject) or isinstance(obj, ogr.MajorObject)
        return obj.GetDescription()

    def writeValue(self, obj, value):
        assert isinstance(obj, gdal.MajorObject) or isinstance(obj, ogr.MajorObject)
        error = None
        try:
            if value is None:
                v = ''
            else:
                v = str(value)

            obj.SetDescription(v)
        except Exception as ex:
            error = ex
        return error

class MDKeyClassification(MDKeyAbstract):
    def __init__(self):
        super(MDKeyClassification, self).__init__('Classification')

    def readValue(self, obj):
        assert isinstance(obj, gdal.MajorObject) or isinstance(obj, ogr.MajorObject)
        from enmapbox.gui.classificationscheme import ClassificationScheme
        classScheme = ClassificationScheme.fromRasterImage(obj)
        return classScheme

    def writeValue(self, obj, value):
        error = None
        from enmapbox.gui.classificationscheme import ClassificationScheme
        if isinstance(value, ClassificationScheme):

            s = ""




        return error
