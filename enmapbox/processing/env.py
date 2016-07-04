import tempfile
import os
import shutil
import rios.applier

class PrintProgress():

    @staticmethod
    def setInfo(msg): print msg

    @staticmethod
    def setConsoleInfo(msg): print 'CONSOLE INFO', msg

    @staticmethod
    def setDebugInfo(msg): print 'DEBUG', msg

    @staticmethod
    def setText(msg): print msg

    @staticmethod
    def setPercentage(p): print str(int(p))+'%'


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


class env():

    filelist = [r'C:\Work\data\model_svc.clf',
                r'C:\Work\data\model_rfc.clf',
                r'C:\Work\data\model_linearsvc.clf']

    tempdir = os.path.join(tempfile.gettempdir(), 'EnMAPBox')


    # workaround for selection dialog in Processing
    isRunning = [1]
    isNotRunning = []

    @staticmethod
    def setRunning(bool):
        if bool:
            env.isRunning = [1]
            env.isNotRunning = []
        else:
            env.isRunning = []
            env.isNotRunning = [1]




    @staticmethod
    def setTempdir(dirname):
        tempdir = dirname
        if not os.path.exists(tempdir):
            os.mkdir(tempdir)


    @staticmethod
    def cleanupTempdir():
        if os.path.exists(tempdir):
            shutil.rmtree(tempdir)
        env.setTempdir(tempdir)


    @staticmethod
    def tempfile(prefix='temp_', suffix=''):
        with tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix) as f:
          basename = os.path.basename(f.name)
        return os.path.join(env.tempdir, basename)


if __name__ == '__main__':
    print tempfile()
    tempdir = r'c:\hallo'
    print tempfile(suffix='.vrt')