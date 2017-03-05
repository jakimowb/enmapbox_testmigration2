import os
from os.path import join, dirname, abspath

class DirectoryLookup(object):

    repository = abspath(join(dirname(__file__), *['..']*3))
    site_packages = join(repository, 'site-packages')
    site_packages_os_specific = join(site_packages, os.sys.platform)
    testdata = join(repository, 'enmapbox', 'testdata')
    ui = join(repository, 'gui', 'ui')