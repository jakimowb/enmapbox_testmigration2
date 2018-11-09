import unittest

class Test(unittest.TestCase):

    def test_version(self):

        from enmapbox.dependencycheck import outdatedTestdata
        self.assertFalse(outdatedTestdata())


if __name__ == "__main__":
    unittest.main()



