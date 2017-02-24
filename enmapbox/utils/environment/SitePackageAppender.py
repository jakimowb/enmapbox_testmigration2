from site import addsitedir
from DirectoryLookup import DirectoryLookup

class SitePackageAppender(object):

    @classmethod
    def appendAll(clf):
        clf.appendRepository()
        clf.appendCrossPlatformSitePackages()
        clf.appendPlatformSpecificSitePackages()

    @classmethod
    def appendRepository(clf):
        addsitedir(DirectoryLookup.repository)

    @classmethod
    def appendCrossPlatformSitePackages(clf):
        addsitedir(DirectoryLookup.site_packages)

    @classmethod
    def appendPlatformSpecificSitePackages(clf):
        addsitedir(DirectoryLookup.site_packages_os_specific)
