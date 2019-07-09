# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/algorithms.py

    Some example algorithms, as they might be implemented somewhere else
    ---------------------
    Date                 : Juli 2017
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

def dummyAlgorithm(*args, **kwds):
    print('Dummy Algorithm started')
    if len(args) > 0:
        print('Print arguments:')
        for i, arg in enumerate(args):
            print('Arg{}:{}'.format(i+1,str(arg)))
    else:
        print('No arguments defined')
    if len(kwds) > 0:
        print('Print keywords:')
        for k, v in kwds.items():
            print('Kwd {}={}'.format(k,str(v)))
    else:
        print('No keywords defined')
    print('Dummy Algorithm finished')
