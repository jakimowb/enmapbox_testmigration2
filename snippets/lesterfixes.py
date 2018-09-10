from qgis.PyQt.QtWidgets import QAction

a = QAction('info')
b = QAction('info', None)

print(a.text())
print(b.text())