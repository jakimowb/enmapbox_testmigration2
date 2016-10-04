from __future__ import absolute_import
import tempfile
import os

class Temporary():

    def __init__(self, root=tempfile.gettempdir()):
        self.root = root

    def path(self, prefix='', suffix=''):
        #return tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=self.root)[1]
        with tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix) as f:
          basename = os.path.basename(f.name)
        return os.path.join(self.root, basename)


if __name__ == '__main__':

    # use default user temp as root
    temp = Temporary()
    print(temp.path())
    print(temp.path(prefix='myFile_', suffix='.txt'))

    # set root explicitely
    temp = Temporary(root=r'c:\myFolder')
    for i in range(10):
        print(temp.path(prefix='hello_', suffix='.txt'))

    print(temp.path('workflow_'))



