from unittest import TestCase
from os.path import join
from TestdataInitPyGenerator import TestdataInitPyGenerator
from enmapbox import DIR_TESTDATA

CODE = \
'''
#NOTE: this file is auto-generated!

import os

root = os.path.dirname(__file__)
HymapBerlinA_image = os.path.join(root, "HymapBerlinA_image")
HymapBerlinA_imagesample = os.path.join(root, "HymapBerlinA_imagesample")
HymapBerlinA_mask = os.path.join(root, "HymapBerlinA_mask")
HymapBerlinA_test = os.path.join(root, "HymapBerlinA_test")
HymapBerlinA_train = os.path.join(root, "HymapBerlinA_train")
HymapBerlinA_trainsample = os.path.join(root, "HymapBerlinA_trainsample")
HymapBerlinA_truth = os.path.join(root, "HymapBerlinA_truth")
'''

class TestTestdataInitGenerator(TestCase):

    def test_generateHymapBerlinA(self):
        root = join(DIR_TESTDATA, 'HymapBerlinA')
        initpy = TestdataInitPyGenerator().generate(root=root, ignore_extensions=['hdr', 'xml', 'py', 'pyc'])
        self.assertEqualTextInFile(text=CODE, filename=initpy)

    def assertEqualTextInFile(self, text, filename):
        with open(filename) as f:
            text_in_file = ''.join(f.readlines())
        self.assertEqual(text, text_in_file)