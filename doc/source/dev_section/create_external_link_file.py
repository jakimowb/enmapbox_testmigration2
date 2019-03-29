import re, os
import qgis.core
import qgis.gui
import PyQt5.QtCore
import PyQt5.QtGui
import PyQt5.QtWidgets

PATH_LINK_RST = os.path.join(os.path.dirname(__file__), 'external_links.rst')
objects = []
for module in [qgis.core, qgis.gui
               , PyQt5.QtCore
               , PyQt5.QtWidgets, PyQt5.QtGui, PyQt5.QtWidgets
               ]:
    s = ""
    for key in module.__dict__.keys():
        if re.search('^(Qgs|Q)', key):
            objects.append(key)
objects = sorted(objects)


lines = """
.. autogenerated file. 

.. _PyCharm: https://www.jetbrains.com/pycharm/
.. _PyQtGraph: http://www.pyqtgraph.org/documentation/
.. _Bitbucket: https://bitbucket.org
.. _Git: https://git-scm.com/
.. _GitHub: https://github.com/
.. _GDAL: https://www.gdal.org
.. _QtWidgets: https://doc.qt.io/qt-5/qtwidgets-index.html
.. _QtCore: https://doc.qt.io/qt-5/qtcore-index.html
.. _QtGui: https://doc.qt.io/qt-5/qtgui-index.html
.. _qgis.gui: https://qgis.org/api/group__gui.html
.. _qgis.core: https://qgis.org/api/group__core.html

.. # autogenerated singular forms 
"""


WRITTEN = []
for obj in objects:

    if obj in ['QtCore', 'QtGui', 'QtWidget']:
        continue
    print(obj)

    target = None
    if obj.startswith('Qgs'):
        # https://qgis.org/api/classQgsProject.html
        target = "https://qgis.org/api/class{}.html".format(obj)
    elif obj.startswith('Q'):
        # https://doc.qt.io/qt-5/qwidget.html
        target = "https://doc.qt.io/qt-5/{}.html".format(obj.lower())
    else:
        continue

    singular = obj
    plural = obj+'s'

    line = None
    if singular.upper() not in WRITTEN:
        line = '.. _{}: {}'.format(singular, target)
        WRITTEN.append(singular.upper())

        if plural.upper() not in WRITTEN:
            line += '\n.. _{}: {}'.format(plural, target)
            WRITTEN.append(plural.upper())

    if line:
        lines += '\n'+line


with open(PATH_LINK_RST, 'w', encoding='utf-8') as f:
    f.write(lines)
