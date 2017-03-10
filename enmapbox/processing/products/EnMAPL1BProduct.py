from os.path import basename, join
from xml.etree import ElementTree


class EnMAPL1BProduct(object):

    def __init__(self, folder):
        self.folder = folder
        self.sceneId, self.level, self.date, self.row = self._parseSceneId()
        self.fheader = join(self.folder, 'E_{self.level}_Berlin_{self.date}_{self.row}_header.txt'.format(self=self))
        self.fdetector1 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D1_{self.row}.bsq'.format(self=self))
        self.fdetector2 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D2_{self.row}.bsq'.format(self=self))
        self.fcloudmask1 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D1_{self.row}_cloudmask.tif'.format(self=self))
        self.fcloudmask2 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D2_{self.row}_cloudmask.tif'.format(self=self))
        self.fdeadpixelmap1 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D1_{self.row}_deadpixelmap.tif'.format(self=self))
        self.fdeadpixelmap2 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D2_{self.row}_deadpixelmap.tif'.format(self=self))
        self.fquicklook1 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D1_{self.row}_quicklook.png'.format(self=self))
        self.fquicklook2 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D2_{self.row}_quicklook.png'.format(self=self))
        self.frpcmodel1 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D1_{self.row}_rpcmodel.tif'.format(self=self))
        # self.frpcmodel2 = join(self.folder, 'E_{self.level}_Berlin_{self.date}_D2_{self.row}_rpcmodel.tif'.format(self=self))
        # Karl, why is there no rpcmodel.tif for D2?

        self.xmlRoot = ElementTree.parse(self.fheader).getroot()

    def getHeaderNode(self, xpath):
        nodes = self.xmlRoot.findall(xpath)
        if len(nodes) == 1:
            return nodes[0]
        elif len(nodes) == 0:
            raise NoMatchError(xpath)
        elif len(nodes) > 1:
            raise MultipleMatchError(xpath)

    def _parseSceneId(self):
        sceneIdWithRow = basename(self.folder)
        _, level, _, date, row = sceneIdWithRow.split('_')
        sceneId = sceneIdWithRow[:-len(row) - 1]
        return sceneId, level, date, row

class NoMatchError(Exception):
    pass

class MultipleMatchError(Exception):
    pass
