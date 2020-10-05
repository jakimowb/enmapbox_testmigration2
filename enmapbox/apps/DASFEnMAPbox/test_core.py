import enmapboxtestdata
from DASFEnMAPbox.core import DASF_retrieval

DASF_retrieval(inputFile='C:\\Users\\Marion\\Desktop\\EnMAP_box\\MyTool\\KROOF03_Viertel_RFC_geo_1m_subset710_790.bsq',
                outputName='DASF.bsq',
               secondoutputName='DASF_RetrievalQuality.bsq',
               thirdoutputName='CSC.bsq')

if True: # show the result in a viewer
    from hubdc.core import openRasterDataset, MapViewer
    rasterDataset = openRasterDataset(filename='DASF.bsq')
    MapViewer().addLayer(rasterDataset.mapLayer()).show()
