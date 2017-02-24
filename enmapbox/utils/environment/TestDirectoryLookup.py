from unittest import TestCase
from os.path import isdir
from DirectoryLookup import DirectoryLookup

class TestDirectoryLookup(TestCase):

    def test_ifAllDirectoriesExist(self):
        dirs = DirectoryLookup
        self.assertIsDir(dirs.repository)
        self.assertIsDir(dirs.site_packages)
        self.assertIsDir(dirs.site_packages_os_specific)
        self.assertIsDir(dirs.testdata)
        self.assertIsDir(dirs.ui)

    def assertIsDir(self, dir):
        return isdir(dir)