# -*- coding: utf-8 -*-

__author__ = 'Benjamin Jakimow'
__date__ = 'March 2016'
__copyright__ = '(C) 2016, Benjamin Jakimow'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

#from pkgutil import extend_path
#__path__ = extend_path(__path__, __name__)

def classFactory(iface):
    from enmapboxplugin import EnMAPBoxPlugin
    return EnMAPBoxPlugin(iface)