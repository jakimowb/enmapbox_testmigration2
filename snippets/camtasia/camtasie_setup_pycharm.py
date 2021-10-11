
import qgis.utils
from enmapbox.testing import TestCase
from enmapbox.gui.enmapboxgui import EnMAPBox
from enmapbox import initAll

class StartEnMAPBoxCamtasia(TestCase):

    @classmethod
    def setUpClass(cls, *args, **kwds) -> None:
        super().setUpClass(*args, **kwds)
        initAll()

    def clearAndResize(self, emb: EnMAPBox):
        emb.messageBar().clearWidgets()
        emb.ui.resize(1280 - 2, 720 - 32)

    def test_start_intro_speclib_empty(self):

        emb = EnMAPBox(load_other_apps=False, load_core_apps=True)

        self.assertIsInstance(EnMAPBox.instance(), EnMAPBox)
        self.assertEqual(emb, EnMAPBox.instance())

        # remove error messages
        self.clearAndResize(emb)

        self.showGui(emb.ui)

