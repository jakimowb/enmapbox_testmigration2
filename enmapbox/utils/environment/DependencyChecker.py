class DependencyChecker(object):

    @staticmethod
    def isImportable(name):

        try:
            exec 'import {package}'.format(package=name)
            return True
        except:
            return False

    @staticmethod
    def importAllDependencies(names):
        for name in names:
            exec 'import {package}'.format(package=name)
