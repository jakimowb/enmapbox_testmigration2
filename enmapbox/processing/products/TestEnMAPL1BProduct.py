from unittest import TestCase
from os.path import join
from .EnMAPL1BProduct import EnMAPL1BProduct, NoMatchError, MultipleMatchError

class TestEnMAPL1BProduct(TestCase):

    def test_initProduct(self):
        sceneFolder = r'C:\Work\data\EnMAP_DatenKarl\E_L1B_Berlin_20160716_1'
        l1B = EnMAPL1BProduct(sceneFolder)
        self.assertEqual(l1B.sceneId, 'E_L1B_Berlin_20160716')
        self.assertEqual(l1B.level, 'L1B')
        self.assertEqual(l1B.date, '20160716')
        self.assertEqual(l1B.row, '1')

        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_1_header.txt'), l1B.fheader)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D1_1.bsq'), l1B.fdetector1)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D1_1_cloudmask.tif'), l1B.fcloudmask1)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D1_1_deadpixelmap.tif'), l1B.fdeadpixelmap1)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D1_1_quicklook.png'), l1B.fquicklook1)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D1_1_rpcmodel.tif'), l1B.frpcmodel1)

        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D2_1.bsq'), l1B.fdetector2)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D2_1_cloudmask.tif'), l1B.fcloudmask2)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D2_1_deadpixelmap.tif'), l1B.fdeadpixelmap2)
        self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D2_1_quicklook.png'), l1B.fquicklook2)
        #self.assertEqual(join(sceneFolder, 'E_L1B_Berlin_20160716_D2_1_rpcmodel.tif'), l1B.rpcmodel2)
        # Karl, why is there no rpcmodel for D2?

    def test_queryInvalidMetadata(self):
        sceneFolder = r'C:\Work\data\EnMAP_DatenKarl\E_L1B_Berlin_20160716_1'
        l1B = EnMAPL1BProduct(sceneFolder)
        with self.assertRaises(NoMatchError) as context:
            l1B.getHeaderNode('detector1/wrong_keys')
        self.assertIsInstance(context.exception, context.expected)


    def test_queryListlikeMetadata(self):
        sceneFolder = r'C:\Work\data\EnMAP_DatenKarl\E_L1B_Berlin_20160716_1'
        l1B = EnMAPL1BProduct(sceneFolder)
        node = l1B.getHeaderNode('detector1/centre_wavelength')

        lead = [float(v) for v in node.text.split(' ') if v.strip() != '']

        gold = [423.03, 428.80, 434.29, 439.58, 444.72, 449.75, 454.70, 459.59, 464.43, 469.25, 474.05, 478.84, 483.63,
                488.42, 493.23, 498.05, 502.90, 507.77, 512.67, 517.60, 522.57, 527.58, 532.63, 537.72, 542.87, 548.06,
                553.30, 558.60, 563.95, 569.36, 574.83, 580.36, 585.95, 591.60, 597.32, 603.10, 608.95, 614.86, 620.84,
                626.90, 633.02, 639.21, 645.47, 651.80, 658.20, 664.67, 671.21, 677.83, 684.51, 691.26, 698.08, 704.97,
                711.92, 718.95, 726.03, 733.19, 740.40, 747.68, 755.01, 762.41, 769.86, 777.37, 784.93, 792.54, 800.20,
                807.91, 815.67, 823.46, 831.30, 839.18, 847.10, 855.05, 863.03, 871.05, 879.09, 887.16, 895.25, 903.36,
                911.49, 919.64, 927.80, 935.98, 944.17, 952.37, 960.57, 968.78, 976.99, 985.21]

        self.assertItemsEqual(gold, lead)

    def test_queryScalarMetadata(self):
        sceneFolder = r'C:\Work\data\EnMAP_DatenKarl\E_L1B_Berlin_20160716_1'
        l1B = EnMAPL1BProduct(sceneFolder)
        node = l1B.getHeaderNode('detector1/geometry/RPC_sensor_model/column_RMSE')

        gold = '{rmse} {unit}'.format(rmse=295.957232, unit='px')
        lead = '{rmse} {unit}'.format(rmse=float(node.text), unit=node.attrib['unit'])

        self.assertEqual(gold, lead)

