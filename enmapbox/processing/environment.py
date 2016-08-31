import tempfile
import os
import shutil

class PrintProgress():

    @staticmethod
    def setInfo(msg): print(msg)

    @staticmethod
    def setConsoleInfo(msg): print('CONSOLE INFO', msg)

    @staticmethod
    def setDebugInfo(msg): print('DEBUG', msg)

    @staticmethod
    def setText(msg): print(msg)

    @staticmethod
    def setPercentage(p): print(str(int(p))+'%')

class SilentProgress():

    @staticmethod
    def setInfo(msg): pass

    @staticmethod
    def setConsoleInfo(msg): pass

    @staticmethod
    def setDebugInfo(msg): pass

    @staticmethod
    def setText(msg): pass

    @staticmethod
    def setPercentage(p): pass


_tempdir = os.path.join(tempfile.gettempdir(), 'EnMAPBox')

class Environment():

    rasterFilenames = [r'< select a raster file >']
    modelFilenames = [r'< select a model file>']
    tempdir = _tempdir

    @staticmethod
    def openRaster(filename):
        if not filename in Environment.rasterFilenames:
            Environment.rasterFilenames.append(filename)

    @staticmethod
    def openModel(filename):
        if not filename in Environment.modelFilenames:
            Environment.modelFilenames.append(filename)

    @staticmethod
    def setTempdir(dirname):
        tempdir = dirname
        if not os.path.exists(tempdir):
            os.mkdir(tempdir)


    @staticmethod
    def cleanupTempdir():
        if os.path.exists(Environment.tempdir):
            shutil.rmtree(Environment.tempdir)
        Environment.setTempdir(Environment.tempdir)


    @staticmethod
    def tempfile(prefix='temp_', suffix=''):
        with tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix) as f:
          basename = os.path.basename(f.name)
        return os.path.join(Environment.tempdir, basename)


if __name__ == '__main__':
    print(Environment.tempfile())
