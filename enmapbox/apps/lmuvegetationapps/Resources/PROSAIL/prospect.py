# -*- coding: utf-8 -*-

from scipy.special import exp1
from lmuvegetationapps.Resources.PROSAIL.dataSpec import *
import numpy as np

class Prospect:

    nlambd = len(lambd)

    def prospect_Pro(self,N,Cab,Car,Anth,Cp,Cbc,Cbrown,Cw):  #Cm

        n = Ppro_refractive
        k = (np.outer(Cab, Ppro_k_Cab) + np.outer(Car, Ppro_k_Ccx) + np.outer(Anth, Ppro_k_Canth) +
             np.outer(Cbrown, Ppro_k_Cbrown) + np.outer(Cw, Ppro_k_Cw) +  # np.outer(Cm, Ppro_k_Cm)
             np.outer(Cp, Ppro_k_Cp) + np.outer(Cbc, Ppro_k_Cbc)) / N[:, np.newaxis]

        ind_k0_row, ind_k0_col = np.where(k == 0)  # Vectorize = 2D

        if len(ind_k0_row) > 0:
            k[ind_k0_row, ind_k0_col] = np.finfo(float).eps
        trans = (1 - k) * np.exp(-k) + (k ** 2) * exp1(k)
        trans2 = trans ** 2

        # t12, tav90n are calculated once and are listet in dataSpec
        # t12 is tav(4 0,n); tav90n is tav(90,n)
        t21 = Ppro_tav90n / (n ** 2)
        r12 = 1 - Ppro_t12
        r21 = 1 - t21
        r21_2 = r21 ** 2
        x = Ppro_t12 / Ppro_tav90n
        y = x * (Ppro_tav90n - 1) + 1 - Ppro_t12

        # reflectance and transmittance of the elementary layer N = 1
        ra = r12 + ((Ppro_t12 * t21 * r21) * trans2) / (1 - (r21_2) * (trans2))
        ta = ((Ppro_t12 * t21) * trans) / (1 - (r21_2) * (trans2))
        r90 = (ra - y) / x
        t90 = ta / x

        # reflectance and transmittance of N layers
        t90_2 = t90 ** 2
        r90_2 = r90 ** 2

        delta = np.sqrt((t90_2 - r90_2 - 1) ** 2 - 4 * r90_2)
        beta = (1 + r90_2 - t90_2 - delta) / (2 * r90)
        va = (1 + r90_2 - t90_2 + delta) / (2 * r90)

        vb = np.zeros((Cab.shape[0], self.nlambd))

        ind_vb_le_row, ind_vb_le_col = np.where(va * (beta - r90) <= 1e-14)
        ind_vb_gt_row, ind_vb_gt_col = np.where(va * (beta - r90) > 1e-14)
        vb[ind_vb_le_row, ind_vb_le_col] = np.sqrt(beta[ind_vb_le_row, ind_vb_le_col] *
                                                   (va[ind_vb_le_row, ind_vb_le_col] - r90[
                                                       ind_vb_le_row, ind_vb_le_col]) / (1e-14))
        vb[ind_vb_gt_row, ind_vb_gt_col] = np.sqrt(beta[ind_vb_gt_row, ind_vb_gt_col] *
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                       ind_vb_gt_row, ind_vb_gt_col]) /
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] *
                                                    (beta[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                        ind_vb_gt_row, ind_vb_gt_col])))

        vbNN = vb ** ((N - 1)[:, np.newaxis])
        vbNNinv = 1 / vbNN
        vainv = 1 / va
        s1 = ta * t90 * (vbNN - vbNNinv)
        s2 = ta * (va - vainv)
        s3 = va * vbNN - vainv * vbNNinv - r90 * (vbNN - vbNNinv)

        RN = ra + s1 / s3
        TN = s2 / s3
        LRT = np.zeros((Cab.shape[0], self.nlambd, 3))
        LRT[:, :, 0] = lambd[np.newaxis, :]
        LRT[:, :, 1] = RN
        LRT[:, :, 2] = TN

        return LRT

    def prospect_Cp(self,N,Cab,Car,Anth,Cp,Ccl,Cbrown,Cw,Cm):

        n = Pcp_refractive
        k = (np.outer(Cab, Pcp_k_Cab) + np.outer(Car, Pcp_k_Car) + np.outer(Anth, Pcp_k_Anth) +
             np.outer(Cbrown, Pcp_k_Brown) + np.outer(Cw, Pcp_k_Cw) + np.outer(Cm, Pcp_k_Cm) +
             np.outer(Cp, Pcp_k_Ccl) + np.outer(Ccl, Pcp_k_Cp)) / N[:, np.newaxis]

        ind_k0_row, ind_k0_col = np.where(k == 0)  # Vectorize = 2D

        if len(ind_k0_row) > 0:
            k[ind_k0_row, ind_k0_col] = np.finfo(float).eps
        trans = (1 - k) * np.exp(-k) + (k ** 2) * exp1(k)
        trans2 = trans ** 2

        # t12, tav90n are calculated once and are listet in dataSpec
        # t12 is tav(4 0,n); tav90n is tav(90,n)
        t21 = Pcp_tav90n / (n ** 2)
        r12 = 1 - Pcp_t12
        r21 = 1 - t21
        r21_2 = r21 ** 2
        x = Pcp_t12 / Pcp_tav90n
        y = x * (Pcp_tav90n - 1) + 1 - Pcp_t12

        # reflectance and transmittance of the elementary layer N = 1
        ra = r12 + ((Pcp_t12 * t21 * r21) * trans2) / (1 - (r21_2) * (trans2))
        ta = ((Pcp_t12 * t21) * trans) / (1 - (r21_2) * (trans2))
        r90 = (ra - y) / x
        t90 = ta / x

        # reflectance and transmittance of N layers
        t90_2 = t90 ** 2
        r90_2 = r90 ** 2

        delta = np.sqrt((t90_2 - r90_2 - 1) ** 2 - 4 * r90_2)
        beta = (1 + r90_2 - t90_2 - delta) / (2 * r90)
        va = (1 + r90_2 - t90_2 + delta) / (2 * r90)

        vb = np.zeros((Cab.shape[0], self.nlambd))

        ind_vb_le_row, ind_vb_le_col = np.where(va * (beta - r90) <= 1e-14)
        ind_vb_gt_row, ind_vb_gt_col = np.where(va * (beta - r90) > 1e-14)
        vb[ind_vb_le_row, ind_vb_le_col] = np.sqrt(beta[ind_vb_le_row, ind_vb_le_col] *
                                                   (va[ind_vb_le_row, ind_vb_le_col] - r90[
                                                       ind_vb_le_row, ind_vb_le_col]) / (1e-14))
        vb[ind_vb_gt_row, ind_vb_gt_col] = np.sqrt(beta[ind_vb_gt_row, ind_vb_gt_col] *
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                       ind_vb_gt_row, ind_vb_gt_col]) /
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] *
                                                    (beta[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                        ind_vb_gt_row, ind_vb_gt_col])))

        vbNN = vb ** ((N - 1)[:, np.newaxis])
        vbNNinv = 1 / vbNN
        vainv = 1 / va
        s1 = ta * t90 * (vbNN - vbNNinv)
        s2 = ta * (va - vainv)
        s3 = va * vbNN - vainv * vbNNinv - r90 * (vbNN - vbNNinv)

        RN = ra + s1 / s3
        TN = s2 / s3
        LRT = np.zeros((Cab.shape[0], self.nlambd, 3))
        LRT[:, :, 0] = lambd[np.newaxis, :]
        LRT[:, :, 1] = RN
        LRT[:, :, 2] = TN

        return LRT


    def prospect_D(self,N,Cab,Car,Anth,Cbrown,Cw,Cm):
        n = PD_refractive
        k = (np.outer(Cab, PD_k_Cab) + np.outer(Car, PD_k_Car) + np.outer(Anth, PD_k_Anth) +
             np.outer(Cbrown, PD_k_Brown) + np.outer(Cw, PD_k_Cw) + np.outer(Cm, PD_k_Cm)) / N[:, np.newaxis]

        ind_k0_row, ind_k0_col = np.where(k == 0)  # Vectorize = 2D

        if len(ind_k0_row) > 0: 
            k[ind_k0_row, ind_k0_col] = np.finfo(float).eps
        trans = (1 - k) * np.exp(-k) + (k ** 2) * exp1(k)
        trans2 = trans ** 2

        # t12, tav90n are calculated once and are listet in dataSpec
        # t12 is tav(4 0,n); tav90n is tav(90,n)
        t21 = PD_tav90n / (n ** 2)
        r12 = 1 - PD_t12
        r21 = 1 - t21
        r21_2 = r21 ** 2
        x = PD_t12 / PD_tav90n
        y = x * (PD_tav90n - 1) + 1 - PD_t12

        # reflectance and transmittance of the elementary layer N = 1
        ra = r12 + ((PD_t12 * t21 * r21) * trans2) / (1 - (r21_2) * (trans2))
        ta = ((PD_t12 * t21) * trans) / (1 - (r21_2) * (trans2))
        r90 = (ra - y) / x
        t90 = ta / x

        # reflectance and transmittance of N layers
        t90_2 = t90 ** 2
        r90_2 = r90 ** 2

        delta = np.sqrt((t90_2 - r90_2 - 1) ** 2 - 4 * r90_2)
        beta = (1 + r90_2 - t90_2 - delta) / (2 * r90)
        va = (1 + r90_2 - t90_2 + delta) / (2 * r90)

        vb = np.zeros((Cab.shape[0], self.nlambd))

        ind_vb_le_row, ind_vb_le_col = np.where(va * (beta-r90) <= 1e-14)
        ind_vb_gt_row, ind_vb_gt_col = np.where(va * (beta-r90) > 1e-14)
        vb[ind_vb_le_row, ind_vb_le_col] = np.sqrt(beta[ind_vb_le_row, ind_vb_le_col] * 
                                                   (va[ind_vb_le_row, ind_vb_le_col] - r90[ind_vb_le_row, ind_vb_le_col]) / (1e-14))
        vb[ind_vb_gt_row, ind_vb_gt_col] = np.sqrt(beta[ind_vb_gt_row, ind_vb_gt_col] * 
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] - r90[ind_vb_gt_row, ind_vb_gt_col]) / 
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] * 
                                                    (beta[ind_vb_gt_row, ind_vb_gt_col] - r90[ind_vb_gt_row, ind_vb_gt_col])))

        vbNN = vb ** ((N - 1)[:, np.newaxis])
        vbNNinv = 1 / vbNN
        vainv = 1 / va
        s1 = ta * t90 * (vbNN - vbNNinv)
        s2 = ta * (va - vainv)
        s3 = va * vbNN - vainv * vbNNinv - r90 * (vbNN - vbNNinv)

        RN = ra + s1 / s3
        TN = s2 / s3
        LRT = np.zeros((Cab.shape[0], self.nlambd, 3))
        LRT[:, :, 0] = lambd[np.newaxis, :]
        LRT[:, :, 1] = RN
        LRT[:, :, 2] = TN

        return LRT

    def prospect_5(self,N,Cab,Car,Cw,Cm):

        n = P5_refractive
        k = (np.outer(Cab, P5_k_Cab) + np.outer(Car, P5_k_Car) + np.outer(Cw, P5_k_Cw) + np.outer(Cm, P5_k_Cm)) / N[:, np.newaxis]

        ind_k0_row, ind_k0_col = np.where(k == 0)  # Vectorize = 2D

        if len(ind_k0_row) > 0:
            k[ind_k0_row, ind_k0_col] = np.finfo(float).eps
        trans = (1 - k) * np.exp(-k) + (k ** 2) * exp1(k)
        trans2 = trans ** 2

        # t12, tav90n are calculated once and are listet in dataSpec
        # t12 is tav(4 0,n); tav90n is tav(90,n)
        t21 = P5_tav90n / (n ** 2)
        r12 = 1 - P5_t12
        r21 = 1 - t21
        r21_2 = r21 ** 2
        x = P5_t12 / P5_tav90n
        y = x * (P5_tav90n - 1) + 1 - P5_t12

        # reflectance and transmittance of the elementary layer N = 1
        ra = r12 + ((P5_t12 * t21 * r21) * trans2) / (1 - (r21_2) * (trans2))
        ta = ((P5_t12 * t21) * trans) / (1 - (r21_2) * (trans2))
        r90 = (ra - y) / x
        t90 = ta / x

        # reflectance and transmittance of N layers
        t90_2 = t90 ** 2
        r90_2 = r90 ** 2

        delta = np.sqrt((t90_2 - r90_2 - 1) ** 2 - 4 * r90_2)
        beta = (1 + r90_2 - t90_2 - delta) / (2 * r90)
        va = (1 + r90_2 - t90_2 + delta) / (2 * r90)

        vb = np.zeros((Cab.shape[0], self.nlambd))

        ind_vb_le_row, ind_vb_le_col = np.where(va * (beta - r90) <= 1e-14)
        ind_vb_gt_row, ind_vb_gt_col = np.where(va * (beta - r90) > 1e-14)
        vb[ind_vb_le_row, ind_vb_le_col] = np.sqrt(beta[ind_vb_le_row, ind_vb_le_col] *
                                                   (va[ind_vb_le_row, ind_vb_le_col] - r90[
                                                       ind_vb_le_row, ind_vb_le_col]) / (1e-14))
        vb[ind_vb_gt_row, ind_vb_gt_col] = np.sqrt(beta[ind_vb_gt_row, ind_vb_gt_col] *
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                       ind_vb_gt_row, ind_vb_gt_col]) /
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] *
                                                    (beta[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                        ind_vb_gt_row, ind_vb_gt_col])))

        vbNN = vb ** ((N - 1)[:, np.newaxis])
        vbNNinv = 1 / vbNN
        vainv = 1 / va
        s1 = ta * t90 * (vbNN - vbNNinv)
        s2 = ta * (va - vainv)
        s3 = va * vbNN - vainv * vbNNinv - r90 * (vbNN - vbNNinv)

        RN = ra + s1 / s3
        TN = s2 / s3
        LRT = np.zeros((Cab.shape[0], self.nlambd, 3))
        LRT[:, :, 0] = lambd[np.newaxis, :]
        LRT[:, :, 1] = RN
        LRT[:, :, 2] = TN

        return LRT

    def prospect_5B(self,N,Cab,Car,Cbrown,Cw,Cm):

        n = P5_refractive
        k = (np.outer(Cab, P5_k_Cab) + np.outer(Car, P5_k_Car) + 
             np.outer(Cbrown, P5_k_Brown) + np.outer(Cw, P5_k_Cw) + np.outer(Cm, P5_k_Cm)) / N[:, np.newaxis]

        ind_k0_row, ind_k0_col = np.where(k == 0)  # Vectorize = 2D

        if len(ind_k0_row) > 0:
            k[ind_k0_row, ind_k0_col] = np.finfo(float).eps
        trans = (1 - k) * np.exp(-k) + (k ** 2) * exp1(k)
        trans2 = trans ** 2

        # t12, tav90n are calculated once and are listet in dataSpec
        # t12 is tav(4 0,n); tav90n is tav(90,n)
        t21 = P5_tav90n / (n ** 2)
        r12 = 1 - P5_t12
        r21 = 1 - t21
        r21_2 = r21 ** 2
        x = P5_t12 / P5_tav90n
        y = x * (P5_tav90n - 1) + 1 - P5_t12

        # reflectance and transmittance of the elementary layer N = 1
        ra = r12 + ((P5_t12 * t21 * r21) * trans2) / (1 - (r21_2) * (trans2))
        ta = ((P5_t12 * t21) * trans) / (1 - (r21_2) * (trans2))
        r90 = (ra - y) / x
        t90 = ta / x

        # reflectance and transmittance of N layers
        t90_2 = t90 ** 2
        r90_2 = r90 ** 2

        delta = np.sqrt((t90_2 - r90_2 - 1) ** 2 - 4 * r90_2)
        beta = (1 + r90_2 - t90_2 - delta) / (2 * r90)
        va = (1 + r90_2 - t90_2 + delta) / (2 * r90)

        vb = np.zeros((Cab.shape[0], self.nlambd))

        ind_vb_le_row, ind_vb_le_col = np.where(va * (beta - r90) <= 1e-14)
        ind_vb_gt_row, ind_vb_gt_col = np.where(va * (beta - r90) > 1e-14)
        vb[ind_vb_le_row, ind_vb_le_col] = np.sqrt(beta[ind_vb_le_row, ind_vb_le_col] *
                                                   (va[ind_vb_le_row, ind_vb_le_col] - r90[
                                                       ind_vb_le_row, ind_vb_le_col]) / (1e-14))
        vb[ind_vb_gt_row, ind_vb_gt_col] = np.sqrt(beta[ind_vb_gt_row, ind_vb_gt_col] *
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                       ind_vb_gt_row, ind_vb_gt_col]) /
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] *
                                                    (beta[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                        ind_vb_gt_row, ind_vb_gt_col])))

        vbNN = vb ** ((N - 1)[:, np.newaxis])
        vbNNinv = 1 / vbNN
        vainv = 1 / va
        s1 = ta * t90 * (vbNN - vbNNinv)
        s2 = ta * (va - vainv)
        s3 = va * vbNN - vainv * vbNNinv - r90 * (vbNN - vbNNinv)

        RN = ra + s1 / s3
        TN = s2 / s3
        LRT = np.zeros((Cab.shape[0], self.nlambd, 3))
        LRT[:, :, 0] = lambd[np.newaxis, :]
        LRT[:, :, 1] = RN
        LRT[:, :, 2] = TN

        return LRT

    def prospect_4(self,N,Cab,Cw,Cm):
        n = P4_refractive
        k = (np.outer(Cab, P4_k_Cab) + np.outer(Cw, P4_k_Cw) + np.outer(Cm, P4_k_Cm)) / N[:, np.newaxis]

        ind_k0_row, ind_k0_col = np.where(k == 0)  # Vectorize = 2D

        if len(ind_k0_row) > 0:
            k[ind_k0_row, ind_k0_col] = np.finfo(float).eps
        trans = (1 - k) * np.exp(-k) + (k ** 2) * exp1(k)
        trans2 = trans ** 2

        # t12, tav90n are calculated once and are listet in dataSpec
        # t12 is tav(4 0,n); tav90n is tav(90,n)
        t21 = P4_tav90n / (n ** 2)
        r12 = 1 - P4_t12
        r21 = 1 - t21
        r21_2 = r21 ** 2
        x = P4_t12 / P4_tav90n
        y = x * (P4_tav90n - 1) + 1 - P4_t12

        # reflectance and transmittance of the elementary layer N = 1
        ra = r12 + ((P4_t12 * t21 * r21) * trans2) / (1 - (r21_2) * (trans2))
        ta = ((P4_t12 * t21) * trans) / (1 - (r21_2) * (trans2))
        r90 = (ra - y) / x
        t90 = ta / x

        # reflectance and transmittance of N layers
        t90_2 = t90 ** 2
        r90_2 = r90 ** 2

        delta = np.sqrt((t90_2 - r90_2 - 1) ** 2 - 4 * r90_2)
        beta = (1 + r90_2 - t90_2 - delta) / (2 * r90)
        va = (1 + r90_2 - t90_2 + delta) / (2 * r90)

        vb = np.zeros((Cab.shape[0], self.nlambd))

        ind_vb_le_row, ind_vb_le_col = np.where(va * (beta - r90) <= 1e-14)
        ind_vb_gt_row, ind_vb_gt_col = np.where(va * (beta - r90) > 1e-14)
        vb[ind_vb_le_row, ind_vb_le_col] = np.sqrt(beta[ind_vb_le_row, ind_vb_le_col] *
                                                   (va[ind_vb_le_row, ind_vb_le_col] - r90[
                                                       ind_vb_le_row, ind_vb_le_col]) / (1e-14))
        vb[ind_vb_gt_row, ind_vb_gt_col] = np.sqrt(beta[ind_vb_gt_row, ind_vb_gt_col] *
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                       ind_vb_gt_row, ind_vb_gt_col]) /
                                                   (va[ind_vb_gt_row, ind_vb_gt_col] *
                                                    (beta[ind_vb_gt_row, ind_vb_gt_col] - r90[
                                                        ind_vb_gt_row, ind_vb_gt_col])))

        vbNN = vb ** ((N - 1)[:, np.newaxis])
        vbNNinv = 1 / vbNN
        vainv = 1 / va
        s1 = ta * t90 * (vbNN - vbNNinv)
        s2 = ta * (va - vainv)
        s3 = va * vbNN - vainv * vbNNinv - r90 * (vbNN - vbNNinv)

        RN = ra + s1 / s3
        TN = s2 / s3
        LRT = np.zeros((Cab.shape[0], self.nlambd, 3))
        LRT[:, :, 0] = lambd[np.newaxis, :]
        LRT[:, :, 1] = RN
        LRT[:, :, 2] = TN

        return LRT
