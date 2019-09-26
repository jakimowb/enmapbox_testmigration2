from .qps.externals.pyqtgraph import *

try:
    from .qps.externals.pyqtgraph import opengl
except Exception as ex:
    print('PyOpenGL is not available.', file=sys.stderr)
