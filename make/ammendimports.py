
import sys,os , re, importlib, types
moduleMembers = {}



import qgis, qgis.core, qgis, qgis.PyQt.QtCore, qgis.PyQt.QtGui, qgis.PyQt.QtWidgets, qgis.PyQt.QtXml, qgis.PyQt.Qt
moduleNames = ['qgis', 'qgis.core', 'qgis.gui',
           'qgis.PyQt.QtCore','qgis.PyQt.QtGui','qgis.PyQt.QtWidgets','qgis.PyQt.QtXml','qgis.PyQt.Qt']

for moduleName in moduleNames:
    __import__(moduleName)
    module = sys.modules[moduleName]
    for member in dir(module):
        if member in moduleNames:
            continue
        if member in ['QtCore']:
            continue
        mname2 = moduleName+'.'+member

        if '__' in member :
            continue
        if member.startswith('Q'):
            assert moduleMembers.get(member) is None, 'Already defined "{1}" in {0}.{1}'.format(moduleMembers[member], member)
            moduleMembers[member] = moduleName

s = ""

def ammendImports(path):

    f = open(path, 'r', encoding='utf-8')
    text = f.read()
    f.close()

    for member in moduleMembers.keys():

        if member in text:
            print(member)



if __name__ == '__main__':

    p = r'C:\Users\geo_beja\Repositories\QGIS_Plugins\enmap-box\enmapbox\gui\utils.py'

    ammendImports(p)
