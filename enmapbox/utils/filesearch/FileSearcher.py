from os import walk
from os.path import isdir, join
from fnmatch import fnmatch
from os import listdir

class FileSearcher(object):

    def __init__(self, root):
        self.root = root
        if not self.rootIsDirectory():
            raise ValueError()

    def search(self, pattern):
        filenames = []
        for bname in listdir(self.root):
            if fnmatch(bname, pattern):
                filenames.append(join(self.root, bname))
        return filenames

    def searchrecursive(self, pattern):
        filenames = []
        for root, dname, fnames in walk(self.root):
            for fname in fnames:
                if fnmatch(fname, pattern):
                    filenames.append(join(root, fname))
        return filenames

    def rootIsDirectory(self):
        try:
            return isdir(self.root)
        except:
            return False
