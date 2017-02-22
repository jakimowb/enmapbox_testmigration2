from os.path import join
from enmapbox import DIR_TESTDATA
from enmapbox.utils.codegen.TestdataInitPyGenerator import TestdataInitPyGenerator

def generate_testdata_initpy():
    for dir in ['HymapBerlinA', 'HymapBerlinB', 'AlpineForeland', 'UrbanGradient']:
        root = join(DIR_TESTDATA, dir)
        print('generated {initpy}'.format(initpy=join(root, '__init__.py')))
        TestdataInitPyGenerator().generate(root=root)

if __name__ == '__main__':
    generate_testdata_initpy()