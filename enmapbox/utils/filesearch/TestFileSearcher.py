from unittest import TestCase
from os.path import join
from FileSearcher import FileSearcher
from enmapbox import DIR_TESTDATA

class TestFileSearcher(TestCase):

    root = join(DIR_TESTDATA, 'HymapBerlinA')
    gold = set([join(root, v) for v in ['HymapBerlinA_imagesample.hdr', 'HymapBerlinA_trainsample.hdr']])

    def test_isCorrectRootDirectory(self):
        self.assertIsInstance(FileSearcher(root=DIR_TESTDATA), FileSearcher)

    def test_isIncorrectRootDirectory(self):
        self.assertRaises(ValueError, FileSearcher, root=None)
        self.assertRaises(ValueError, FileSearcher, root=r'c:\this path should not exist, right?')
        self.assertRaises(ValueError, FileSearcher, root=dict())

    def test_searchForHymapBerlinATrainingSampleENVIHeaders(self):
        lead_correctcase = set(FileSearcher(root=self.root).search(pattern='*sample.hdr'))
        lead_mixedcase = set(FileSearcher(root=self.root).search(pattern='*SAMple.hDR'))
        self.assertEqual(self.gold, lead_correctcase)
        self.assertEqual(self.gold, lead_mixedcase)

    def test_searchRecursivelyForHymapBerlinATrainingSampleENVIHeaders(self):
        lead_correctcase = set(FileSearcher(root=DIR_TESTDATA).searchrecursive(pattern='*sample.hdr'))
        lead_mixedcase = set(FileSearcher(root=DIR_TESTDATA).searchrecursive(pattern='*SAMple.hDR'))
        self.assertEqual(self.gold, lead_correctcase)
        self.assertEqual(self.gold, lead_mixedcase)

