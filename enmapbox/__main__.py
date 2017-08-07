# -*- coding: utf-8 -*-

"""
***************************************************************************
    __main__
    ---------------------
    Date                 : August 2017
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

if __name__ == '__main__':

    args = sys.argv[1:]

    if '--test' in args:
        # get rid of orphaned cache files first
        pg.renamePyc(path)

        files = buildFileList(examples)
        if '--pyside' in args:
            lib = 'PySide'
        elif '--pyqt' in args or '--pyqt4' in args:
            lib = 'PyQt4'
        elif '--pyqt5' in args:
            lib = 'PyQt5'
        else:
            lib = ''

        exe = sys.executable
        print("Running tests:", lib, sys.executable)
        for f in files:
            testFile(f[0], f[1], exe, lib)
    else:
        run()
