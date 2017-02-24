import os
from os.path import join, dirname

class DirectoryLookup(object):

    repository = dirname(dirname(__file__))
    site_packages = join(repository, 'site-packages')
    site_packages_os_specific = join(site_packages, os.sys.platform)
    testdata = join(repository, 'testdata')
    ui = join(repository, 'gui', 'ui')
