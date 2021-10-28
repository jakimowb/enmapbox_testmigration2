from qgis._gui import QgsMessageViewer
from qgis.testing import start_app

app = start_app()
viewer = QgsMessageViewer()
viewer.setWindowTitle('Test')
html = r"""
EnMAPBoxApplication error(s):
<br /><b>enpt_app:</b>
<p>
<code>ModuleNotFoundError:No module named 'enpt_enmapboxapp'<br />
Traceback:<br />
  File "C:\Users\geo_beja\Repositories\enmap-box\enmapbox\gui\applications.py", line 286, in addApplicationFolder<br />
    apps = factory(self.mEnMAPBox)<br />
  File "C:\Users\geo_beja\Repositories\enmap-box\enmapbox\apps\enpt_app\__init__.py", line 8, in enmapboxApplicationFactory<br />
    from enpt_enmapboxapp.enpt_enmapboxapp import EnPTEnMAPBoxApp<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
</code>
</p>
<br /><b>ensomap:</b>
<p>
<code>ModuleNotFoundError:No module named 'importlib_metadata'<br />
Traceback:<br />
  File "C:\Users\geo_beja\Repositories\enmap-box\enmapbox\gui\applications.py", line 286, in addApplicationFolder<br />
    apps = factory(self.mEnMAPBox)<br />
  File "C:\Users\geo_beja\Repositories\enmap-box\enmapbox\apps\ensomap\__init__.py", line 35, in enmapboxApplicationFactory<br />
    from ensomap.enmapboxintegration import EnSoMAP<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "C:\Users\geo_beja\Repositories\enmap-box\enmapbox\apps\ensomap\enmapboxintegration.py", line 32, in <module><br />
    import hys<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "C:\Users\geo_beja\Repositories\enmap-box\enmapbox\apps\ensomap\hys\__init__.py", line 26, in <module><br />
    from .tools import *<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "C:\Users\geo_beja\Repositories\enmap-box\enmapbox\apps\ensomap\hys\tools.py", line 5, in <module><br />
    from numba import jit, float32, void, intc, int64, int32<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\__init__.py", line 36, in <module><br />
    from numba.core.decorators import (cfunc, generated_jit, jit, njit, stencil,<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\core\decorators.py", line 12, in <module><br />
    from numba.stencils.stencil import stencil<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\stencils\stencil.py", line 11, in <module><br />
    from numba.core import types, typing, utils, ir, config, ir_utils, registry<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\core\registry.py", line 4, in <module><br />
    from numba.core import utils, typing, dispatcher, cpu<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\core\dispatcher.py", line 15, in <module><br />
    from numba.core import utils, types, errors, typing, serialize, config, compiler, sigutils<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\core\compiler.py", line 6, in <module><br />
    from numba.core import (utils, errors, typing, interpreter, bytecode, postproc,<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\core\cpu.py", line 16, in <module><br />
    import numba.core.entrypoints<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
  File "F:\OSGeo4W\apps\Python39\lib\site-packages\numba\core\entrypoints.py", line 4, in <module><br />
    from importlib_metadata import entry_points<br />
  File "F:\OSGeo4W\apps\qgis-dev\python\qgis\utils.py", line 799, in _import<br />
    mod = _builtin_import(name, globals, locals, fromlist, level)<br />
</code>
</p>
"""
viewer.setMessageAsHtml(html)
viewer.show()
app.exec_()