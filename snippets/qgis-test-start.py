"""
How to start the EnMAP-Box from QGIS shell
"""
import site

site.addsitedir(r'/home/jakimowb/repositories/enmap-box')
import enmapbox
import enmapbox.dependencycheck

box = enmapbox.EnMAPBox()

pkgs = enmapbox.dependencycheck.requiredPackages(return_tuples=True)
for i, t in enumerate(pkgs): print(i, t[0])
for t in pkgs:
    pp = enmapbox.dependencycheck.PIPPackage('foobar')
box = enmapbox.EnMAPBox(load_other_apps=False, load_core_apps=True)
