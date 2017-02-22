from os import listdir
from os.path import join

class TestdataInitPyGenerator(object):

    def generate(self, root, ignore_extensions=['hdr', 'xml', 'py', 'pyc']):
        self.root = root
        self.ignore_extensions = ignore_extensions
        code = self._generateCode()
        return self._generateInitPy(code)

    def _generateCode(self):
        return self._makeHeader() + self._makeImports() + self._makeBody()

    def _generateInitPy(self, code):
        initpy = join(self.root, '__init__.py')
        with open(initpy, 'w') as f:
            f.write(code)
        return initpy

    def _makeHeader(self):
        return '\n#NOTE: this file is auto-generated!\n'

    def _makeImports(self):
        return '\nimport os\n'

    def _makeBody(self):
        body = '\nroot = os.path.dirname(__file__)\n'
        for basename in listdir(self.root):
            if not self._isIgnored(basename, self.ignore_extensions):
                body += self._stripExtension(basename) + ' = os.path.join(root, "' + basename + '")\n'
        return body

    def _isIgnored(self, basename, ignore_extensions):
        for ext in ignore_extensions:
            if basename.endswith(ext):
                return True
        return False

    def _stripExtension(self, basename):
        return basename.split('.')[0]

