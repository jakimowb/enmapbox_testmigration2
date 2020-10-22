# -*- coding: utf-8 -*-

'''
Contains supplementary data to save computation time

References:
Verhoef W., Xiao Q., Jia L., & Su Z. (2007):
Unified optical-thermal four-stream radiative transfer theory for homogeneous vegetation canopies.
IEEE Transactions on Geoscience and Remote Sensing, 45, 1808-1822. Article.

Verhoef W., & Bach H. (2003): Simulation of hyperspectral and directional radiance images using coupled biophysical and
atmospheric radiative transfer models. Remote Sensing of Environment, 87, 23-41. Article.

Verhoef W. (1984), Light scattering by leaf layers with application to canopy reflectance modeling: the SAIL model.
Remote Sensing of Environment, 16, 125-141. Article.
'''
import numpy as np

beta_dict = np.array([[0.015192247821401716, 0.04511513125626976, 0.07366721933874043, 0.09998095795183792, 0.12325683701156054, 0.14278760558390557, 0.1579798610972386, 0.16837196070089022, 0.034475081609994906, 0.034644632694447175, 0.03477199446646273, 0.03485697201080851, 0.03489949845644191],
            [0.00028378419874902573, 0.0020294058823425495, 0.005751638473401871, 0.01200202743766678, 0.02190796087454504, 0.03787410106306353, 0.06589705963563201, 0.12690963854753423, 0.04115845607276447, 0.05181790293362443, 0.06942677499148037, 0.106277087297172, 0.4586641625920237],
            [0.0011565951416267486, 0.008876829634519247, 0.029891034176080182, 0.09640335028409708, 0.7273443849356243, 0.09640334777606041, 0.029891033573473225, 0.008876829401686992, 0.000569757676969429, 0.0003409834748974161, 0.000173365433308037, 6.345407373831158e-05, 9.034417918662996e-06],
            [0.42712701495904715, 0.051885576869933114, 0.016954996965587388, 0.003890519113906976, 0.00028378419874897087, 0.0038905192522350474, 0.016954997336226962, 0.05188557794898474, 0.019952583631293264, 0.02655232968560639, 0.0375291397600469, 0.0606223355617268, 0.2824706247166563],
            [0.03789183438420043, 0.043216944609998746, 0.05490877250501834, 0.07525964096053808, 0.10741859382700167, 0.14983497911429472, 0.1813652598851876, 0.18082510675991648, 0.03458082011568342, 0.03411370192811436, 0.033742780197829614, 0.0334862403361027, 0.033355325376113854],
            [0.11111111416724702, 0.11111110780104928, 0.11111111416724703, 0.11111110780104927, 0.111111114167247, 0.11111110780104927, 0.11111111416724706, 0.11111110780104927, 0.022222225379928462, 0.022222219013730782, 0.022222225379928573, 0.02222221901373067, 0.022222223339496305]])

# COS and TAN**2 of angles from 10° to 90° (rad)
cos_tl1 = np.array([0.98480775301220802, 0.93969262078590843, 0.86602540378443871, 0.76604444311897801, 0.64278760968653936,
           0.50000000000000011, 0.34202014332566882, 0.17364817766693041, 0.13917310096006547, 0.10452846326765346,
           0.069756473744125233, 0.03489949670250108, 6.123233995736766e-17])

tan_tl1 = np.array([0.03109120412576338, 0.13247433143179421, 0.33333333333333331, 0.70408819104184717, 1.4202766254612063,
           2.9999999999999982, 7.5486321704130273, 32.163437477526323, 50.628486286221907, 90.523130967774264,
           204.50905538585954, 820.03500208328956, 2.6670937881135714e+32])

# COS and TAN**2 of Angles from 0° to 88° (rad)
cos_tl2 = np.array([1.0, 0.98480775301220802, 0.93969262078590843, 0.86602540378443871, 0.76604444311897801,
           0.64278760968653936, 0.50000000000000011, 0.34202014332566882, 0.17364817766693041, 0.13917310096006547,
           0.10452846326765346, 0.069756473744125233, 0.03489949670250108])

tan_tl2 = np.array([0.0, 0.03109120412576338, 0.13247433143179421, 0.33333333333333331, 0.70408819104184717, 1.4202766254612063,
           2.9999999999999982, 7.5486321704130273, 32.163437477526323, 50.628486286221907, 90.523130967774264,
           204.50905538585954, 820.03500208328956])