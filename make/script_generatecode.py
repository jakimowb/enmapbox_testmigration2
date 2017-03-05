from os.path import join
from enmapbox.utils.environment.DirectoryLookup import DirectoryLookup
from enmapbox.utils.codegen.TestdataInitPyGenerator import TestdataInitPyGenerator

def generate_testdata_initpy():
    for name in ['HymapBerlinA', 'HymapBerlinB', 'UrbanGradient']:
        root = join(DirectoryLookup.testdata, name)
        print('generated {initpy}'.format(initpy=join(root, '__init__.py')))
        TestdataInitPyGenerator().generate(root=root)

if __name__ == '__main__':
    generate_testdata_initpy()