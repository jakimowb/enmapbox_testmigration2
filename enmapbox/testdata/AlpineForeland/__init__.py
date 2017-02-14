import os, sys, re

from enmapbox import jp, file_search

# make testfile locations available as attributes
for file in  file_search(os.path.dirname(__file__), 'AF_*.bsq') + \
             file_search(os.path.dirname(__file__), 'AF_*.bip'):
    bn, ext = os.path.splitext(os.path.basename(file))
    setattr(sys.modules[__name__], bn, file)


