# settings for EnMAP-Box Camtasia reccordings of

# resize to standard video size 1280 x 720
from enmapbox import EnMAPBox
emb = EnMAPBox.instance()
if not isinstance(emb, EnMAPBox):
    emb = EnMAPBox()
    emb.ui.show()

# remove error messages
emb.messageBar().clearWidgets()
emb.ui.resize(1280-2, 720-32)