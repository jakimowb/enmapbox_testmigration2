import os
import pathlib
import shutil

from PyQt5.QtCore import QSize

import qgis.utils
from enmapbox.testing import TestCase
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox import initAll, DIR_ENMAPBOX

class StartEnMAPBoxCamtasia(TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwds) -> None:
        super().setUpClass(*args, **kwds)
        initAll()

    def clearAndResize(self, emb: EnMAPBox):
        emb.messageBar().clearWidgets()
        emb.ui.resize(1280 - 2, 720 - 32)

    def test_start_intro_speclib_empty(self):

        PATH_EXAMPLE = pathlib.Path(DIR_ENMAPBOX) / 'exampledata'
        _PATH_EXAMPLE = PATH_EXAMPLE.parent / ('_'+PATH_EXAMPLE.name)
        rename = PATH_EXAMPLE.is_dir()
        rename = False
        if rename:
            if _PATH_EXAMPLE.is_dir():
                shutil.rmtree(PATH_EXAMPLE)
            else:
                os.rename(PATH_EXAMPLE, _PATH_EXAMPLE)
        emb = EnMAPBox(load_other_apps=False, load_core_apps=True)

        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(emb, EnMAPBox.instance())

        # remove error messages
        self.clearAndResize(emb)
        size = emb.ui.spectralProfileSourcePanel
        emb.ui.spectralProfileSourcePanel.resize(QSize(400, size.height()))

        self.showGui(emb.ui)

        if rename:
            os.rename(_PATH_EXAMPLE, PATH_EXAMPLE)
