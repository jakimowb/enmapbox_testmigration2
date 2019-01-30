import unittest

class Test(unittest.TestCase):

    def test_version(self):

        from enmapbox.dependencycheck import outdatedTestData
        self.assertFalse(outdatedTestData())


if __name__ == "__main__":
    unittest.main()



