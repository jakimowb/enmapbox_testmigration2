import os
from os.path import join, dirname

class DirectoryLookup(object):

    repository = join(dirname(__file__), *['..']*3)
    site_packages = join(repository, 'site-packages')
    site_packages_os_specific = join(site_packages, os.sys.platform)
    testdata = join(repository, 'testdata')
    ui = join(repository, 'gui', 'ui')