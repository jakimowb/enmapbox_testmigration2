from unittest import TestCase

from osgeo import gdal

from hubdsm.algorithm.importenmapl1b import importEnmapL1B


class TestImportEnmapL1B(TestCase):

    def test(self):
        dsVnir, dsSwir = importEnmapL1B(
            filenameMetadataXml=r'C:\Users\janzandr\Downloads\ENMAP01-____L1B-DT000000987_20130205T105307Z_001_V000101_20190426T143700Z__rows100-199\ENMAP01-____L1B-DT000000987_20130205T105307Z_001_V000101_20190426T143700Z-METADATA.XML')
        self.assertEqual(
            dsVnir.GetMetadataItem('wavelength', 'ENVI'),
            '{423.03, 428.8, 434.29, 439.58, 444.72, 449.75, 454.7, 459.59, 464.43, 469.25, 474.05, 478.84, 483.63, 488.42, 493.23, 498.05, 502.9, 507.77, 512.67, 517.6, 522.57, 527.58, 532.63, 537.72, 542.87, 548.06, 553.3, 558.6, 563.95, 569.36, 574.83, 580.36, 585.95, 591.6, 597.32, 603.1, 608.95, 614.86, 620.84, 626.9, 633.02, 639.21, 645.47, 651.8, 658.2, 664.67, 671.21, 677.83, 684.51, 691.26, 698.08, 704.97, 711.92, 718.95, 726.03, 733.19, 740.4, 747.68, 755.01, 762.41, 769.86, 777.37, 784.93, 792.54, 800.2, 807.91, 815.67, 823.46, 831.3, 839.18, 847.1, 855.05, 863.03, 871.05, 879.09, 887.16, 895.25, 903.36, 911.49, 919.64, 927.8, 935.98, 944.17, 952.37, 960.57, 968.78, 976.99, 985.21}'
        )
        self.assertEqual(
            dsSwir.GetMetadataItem('wavelength', 'ENVI'),
            '{904.78, 914.44, 924.23, 934.16, 944.23, 954.42, 964.74, 975.17, 985.73, 996.4, 1007.2, 1018.1, 1029.1, 1040.2, 1051.3, 1062.6, 1074.0, 1085.4, 1096.9, 1108.5, 1120.1, 1131.8, 1143.5, 1155.3, 1167.1, 1179.0, 1190.9, 1202.8, 1214.8, 1226.7, 1238.7, 1250.7, 1262.7, 1274.7, 1286.7, 1298.7, 1310.7, 1322.7, 1334.7, 1346.6, 1358.5, 1370.4, 1382.3, 1487.8, 1499.4, 1510.9, 1522.3, 1533.7, 1545.1, 1556.4, 1567.7, 1578.9, 1590.1, 1601.2, 1612.3, 1623.3, 1634.3, 1645.3, 1656.2, 1667.0, 1677.8, 1688.5, 1699.2, 1709.9, 1720.5, 1731.0, 1741.5, 1752.0, 1762.4, 1772.7, 1941.5, 1951.0, 1960.5, 1969.9, 1979.3, 1988.7, 1998.0, 2007.2, 2016.4, 2025.6, 2034.8, 2043.9, 2052.9, 2061.9, 2070.9, 2079.9, 2088.8, 2097.6, 2106.4, 2115.2, 2124.0, 2132.7, 2141.3, 2150.0, 2158.6, 2167.1, 2175.7, 2184.2, 2192.6, 2201.0, 2209.4, 2217.8, 2226.1, 2234.4, 2242.6, 2250.8, 2259.0, 2267.2, 2275.3, 2283.4, 2291.4, 2299.4, 2307.4, 2315.4, 2323.3, 2331.2, 2339.1, 2346.9, 2354.7, 2362.5, 2370.2, 2377.9, 2385.6, 2393.3, 2400.9, 2408.5, 2416.1, 2423.6, 2431.1, 2438.6}'
        )
        profile = list(dsVnir.ReadAsArray(0, 0, 1, 1).flatten())
        profileScaled = [round(v * dsVnir.GetRasterBand(i + 1).GetScale() + dsVnir.GetRasterBand(i + 1).GetOffset(), 4)
                         for i, v in enumerate(profile)]
        self.assertListEqual(
            profile,
            [1603, 1550, 1585, 1772, 1818, 1891, 1870, 1805, 1846, 1829, 1810, 1941, 1912, 1919, 1789, 1887, 1952, 1943,
             2057, 2415, 2413, 2644, 2789, 2954, 2978, 3034, 3133, 3167, 3126, 3174, 3019, 2964, 2973, 2827, 2816, 2888,
             2781, 2855, 2640, 2583, 2470, 2445, 2345, 2222, 2237, 2179, 2262, 2431, 2701, 3132, 4223, 5405, 6928, 7108,
             9164, 11473, 12420, 12853, 12948, 13292, 14093, 14399, 14462, 14895, 14687, 15040, 15255, 15317, 15052,
             14820, 14699, 14495, 13900, 13802, 13442, 13429, 13319, 13310, 13495, 13391, 13487, 13618, 13419, 13687,
             13293, 13446, 13611, 13845]
        )
        self.assertListEqual(
            profileScaled,
            [0.0542, 0.0485, 0.0467, 0.0503, 0.0519, 0.0538, 0.0542, 0.0522, 0.0514, 0.0499, 0.0485, 0.0476, 0.0456,
             0.042, 0.0414, 0.0408, 0.0388, 0.0382, 0.0375, 0.036, 0.036, 0.037, 0.0369, 0.0364, 0.0349, 0.0347, 0.0345,
             0.0327, 0.031, 0.0305, 0.0287, 0.0282, 0.0271, 0.0248, 0.0244, 0.0243, 0.0231, 0.0224, 0.0211, 0.0203,
             0.0195, 0.0195, 0.0184, 0.0176, 0.0171, 0.0167, 0.0167, 0.017, 0.0174, 0.0185, 0.0225, 0.0269, 0.0317,
             0.0321, 0.0367, 0.0465, 0.0582, 0.0652, 0.0642, 0.0458, 0.068, 0.0766, 0.0747, 0.0734, 0.0709, 0.0694,
             0.0581, 0.0576, 0.0614, 0.0667, 0.0683, 0.0666, 0.0653, 0.0654, 0.0642, 0.0628, 0.0525, 0.0457, 0.0416,
             0.0431, 0.0333, 0.0154, 0.0166, 0.0188, 0.024, 0.0345, 0.0385, 0.0452]
        )
