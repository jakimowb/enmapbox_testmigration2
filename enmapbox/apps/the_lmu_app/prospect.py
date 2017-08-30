# -*- coding: utf-8 -*-
# PROSPECT - reflectance model for deciduous leaves
#
# SUBROUTINES
# tav.py
# _______________________________________________________________________

# Plant leaf reflectance and transmittance are calculated from 400 nm to
# 2500 nm (1 nm step) with the following parameters:

#       - N   = leaf structure parameter
#       - Cab = chlorophyll a+b content in mug/cm^2
#       - Car = carotenoids content in mug/cm^2
#       - Cw  = equivalent water thickness in g/cm^2 or cm
#       - Cm  = dry matter content in g/cm^2

# Here are some examples observed during the LOPEX'93 experiment on
# fresh (F) and dry (D) leaves :

# ---------------------------------------------
 #               N     Cab     Cw        Cm    
# ---------------------------------------------
# min          1.000    0.0  0.004000  0.001900
# max          3.000  100.0  0.040000  0.016500
# corn (F)     1.518   58.0  0.013100  0.003662
# rice (F)     2.275   23.7  0.007500  0.005811
# clover (F)   1.875   46.7  0.010000  0.003014
# laurel (F)   2.660   74.1  0.019900  0.013520
# ---------------------------------------------
# min          1.500    0.0  0.000063  0.0019
# max          3.600  100.0  0.000900  0.0165
# bamboo (D)   2.698   70.8  0.000117  0.009327
# lettuce (D)  2.107   35.2  0.000244  0.002250
# walnut (D)   2.656   62.8  0.000263  0.006573
# chestnut (D) 1.826   47.7  0.000307  0.004305
# ---------------------------------------------
# _______________________________________________________________________

from scipy.special import exp1
from dataSpec import *
import numpy as np

class Prospect:

    nlambd = len(lambd)

    def prospect_D(self,N,Cab,Car,Anth,Cbrown,Cw,Cm):

        n = PD_refractive
        k = (Cab*PD_k_Cab + Car*PD_k_Car + Anth*PD_k_Anth + Cbrown*PD_k_Brown + Cw*PD_k_Cw + Cm*PD_k_Cm) / N
        ind_k0 = np.where(k==0)
        if not len(ind_k0[0])==0: k[ind_k0] = np.finfo(float).eps
        trans = (1-k)*np.exp(-k)+(k**2)*exp1(k)
        trans2 = trans**2

        # reflectance and transmittance of one layer

        # reflectivity and transmissivity at the interface

        # t12, tav90n are calculated once and are listet in dataSpec
        # t12 is tav(4 0,n); tav90n is tav(90,n)
        t21=PD_tav90n/(n**2)
        r12=1-PD_t12
        r21=1-t21
        r21_2 = r21**2
        x=PD_t12/PD_tav90n
        y=x*(PD_tav90n-1)+1-PD_t12

        # reflectance and transmittance of the elementary layer N = 1
        ra=r12+(PD_t12*t21*r21*trans2)/(1-(r21_2)*(trans2))
        ta=(PD_t12*t21*trans)/(1-(r21_2)*(trans2))
        r90=(ra-y)/x
        t90=ta/x

        # reflectance and transmittance of N layers

        t90_2 = t90**2
        r90_2 = r90**2

        delta=np.sqrt((t90_2-r90_2-1)**2-4*r90_2)
        beta=(1+r90_2-t90_2-delta)/(2*r90)
        va=(1+r90_2-t90_2+delta)/(2*r90)

        vb = np.zeros(self.nlambd)



        # # old method, causes a warning:
        # ind_vb_le = np.where(va*(beta-r90)<=1e-14)
        # ind_vb_gt = np.where(va*(beta-r90)>1e-14)
        # vb[ind_vb_le]=np.sqrt(beta*(va-r90)/(1e-14))
        # vb[ind_vb_gt]=np.sqrt(beta*(va-r90)/(va*(beta-r90)))

        # # new method:

        vb = np.where(va * (beta - r90) <= 1e-14, \
                      np.sqrt(beta * (va - r90) / (1e-14)), \
                      vb)
        vb = np.where(va * (beta - r90) > 1e-14, \
                      np.sqrt(beta * (va - r90) / (va * (beta - r90))),
                      vb)

        vbNN = vb**(N-1)
        vbNNinv = 1/vbNN
        vainv = 1/va
        s1=ta*t90*(vbNN-vbNNinv)
        s2=ta*(va-vainv)
        s3=va*vbNN-vainv*vbNNinv-r90*(vbNN-vbNNinv)

        RN=ra+s1/s3
        TN=s2/s3
        LRT = np.zeros((self.nlambd, 3))
        LRT[:,0] = lambd
        LRT[:,1] = RN
        LRT[:,2] = TN

        return LRT

    def prospect_5(self,N,Cab,Car,Cw,Cm):

        n = P5_refractive
        k = (Cab*P5_k_Cab + Car*P5_k_Car + Cw*P5_k_Cw + Cm*P5_k_Cm) / N
        ind_k0 = np.where(k==0)
        if not len(ind_k0[0])==0: k[ind_k0] = np.finfo(float).eps
        trans=(1-k)*np.exp(-k)+(k**2)*exp1(k)


        # reflectance and transmittance of one layer

        # reflectivity and transmissivity at the interface

        t21=P5_tav90n/(n**2)
        r12=1-P5_t12
        r21=1-t21
        x=P5_t12/P5_tav90n
        y=x*(P5_tav90n-1)+1-P5_t12


        # reflectance and transmittance of the elementary layer N = 1

        ra=r12+(P5_t12*t21*r21*trans**2)/(1-(r21**2)*(trans**2))
        ta=(P5_t12*t21*trans)/(1-(r21**2)*(trans**2))
        r90=(ra-y)/x
        t90=ta/x

        # reflectance and transmittance of N layers

        t90_2 = t90**2
        r90_2 = r90**2

        delta=np.sqrt((t90_2-r90_2-1)**2-4*r90_2)
        beta=(1+r90_2-t90_2-delta)/(2*r90)
        va=(1+r90_2-t90_2+delta)/(2*r90)

        vb = np.zeros(self.nlambd)
        ind_vb_le = np.where(va*(beta-r90)<=1e-14)
        ind_vb_gt = np.where(va*(beta-r90)>1e-14)
        vb[ind_vb_le]=np.sqrt(beta*(va-r90)/(1e-14))
        vb[ind_vb_gt]=np.sqrt(beta*(va-r90)/(va*(beta-r90)))

        vbNN = vb**(N-1)
        vbNNinv = 1/vbNN
        vainv = 1/va
        s1=ta*t90*(vbNN-vbNNinv)
        s2=ta*(va-vainv)
        s3=va*vbNN-vainv*vbNNinv-r90*(vbNN-vbNNinv)

        RN=ra+s1/s3
        TN=s2/s3
        LRT = np.zeros((self.nlambd, 3))
        LRT[:,0] = lambd
        LRT[:,1] = RN
        LRT[:,2] = TN

        return LRT


    def prospect_5B(self,N,Cab,Car,Cbrown,Cw,Cm):

        n = P5_refractive
        k = (Cab*P5_k_Cab + Car*P5_k_Car + Cbrown*P5_k_Brown + Cw*P5_k_Cw + Cm*P5_k_Cm) / N
        ind_k0 = np.where(k==0)
        if not len(ind_k0[0])==0: k[ind_k0] = np.finfo(float).eps
        trans=(1-k)*np.exp(-k)+(k**2)*exp1(k)


        # reflectance and transmittance of one layer

        # reflectivity and transmissivity at the interface

        t21=P5_tav90n/(n**2)
        r12=1-P5_t12
        r21=1-t21
        x=P5_t12/P5_tav90n
        y=x*(P5_tav90n-1)+1-P5_t12

        # reflectance and transmittance of the elementary layer N = 1

        ra=r12+(P5_t12*t21*r21*trans**2)/(1-(r21**2)*(trans**2))
        ta=(P5_t12*t21*trans)/(1-(r21**2)*(trans**2))
        r90=(ra-y)/x
        t90=ta/x

        # reflectance and transmittance of N layers

        t90_2 = t90**2
        r90_2 = r90**2

        delta=np.sqrt((t90_2-r90_2-1)**2-4*r90_2)
        beta=(1+r90_2-t90_2-delta)/(2*r90)
        va=(1+r90_2-t90_2+delta)/(2*r90)

        vb = np.zeros(self.nlambd)
        ind_vb_le = np.where(va*(beta-r90)<=1e-14)
        ind_vb_gt = np.where(va*(beta-r90)>1e-14)
        vb[ind_vb_le]=np.sqrt(beta*(va-r90)/(1e-14))
        vb[ind_vb_gt]=np.sqrt(beta*(va-r90)/(va*(beta-r90)))

        vbNN = vb**(N-1)
        vbNNinv = 1/vbNN
        vainv = 1/va
        s1=ta*t90*(vbNN-vbNNinv)
        s2=ta*(va-vainv)
        s3=va*vbNN-vainv*vbNNinv-r90*(vbNN-vbNNinv)

        RN=ra+s1/s3
        TN=s2/s3
        LRT = np.zeros((len(lambd), 3))
        LRT[:,0] = lambd
        LRT[:,1] = RN
        LRT[:,2] = TN

        return LRT

    def prospect_4(self,N,Cab,Cw,Cm):

        n=P4_refractive
        k=(Cab*P4_k_Cab+Cw*P4_k_Cw+Cm*P4_k_Cm)/N
        ind_k0 = np.where(k==0)
        if not len(ind_k0[0])==0: k[ind_k0] = np.finfo(float).eps
        trans=(1-k)*np.exp(-k)+(k**2)*exp1(k)


        # reflectance and transmittance of one layer

        # reflectivity and transmissivity at the interface

        t21=P4_tav90n/(n**2)
        r12=1-P4_t12
        r21=1-t21
        x=P4_t12/P4_tav90n # macht das sinn, die jeweils abzuspeichern, sonst wird die Funktion ja dauernd aufgerufen?
        y=x*(P4_tav90n-1)+1-P4_t12

        # reflectance and transmittance of the elementary layer N = 1

        trans2 = trans**2

        ra=r12+(P4_t12*t21*r21*trans2)/(1-(r21**2)*(trans2))
        ta=(P4_t12*t21*trans)/(1-(r21**2)*(trans2))
        r90=(ra-y)/x
        t90=ta/x

        # reflectance and transmittance of N layers

        r90_2 = r90**2
        t90_2 = t90**2

        delta=np.sqrt((t90_2-r90_2-1)**2-4*r90_2)
        beta=(1+r90_2-t90_2-delta)/(2*r90)
        va=(1+r90_2-t90_2+delta)/(2*r90)

        vb = np.zeros(self.nlambd)

        #Proposal BJ to avoid deprecation warning
        vb = np.where(va*(beta-r90)<=1e-14,np.sqrt(beta*(va-r90)/(1e-14)), vb )
        vb = np.where(va*(beta-r90)>1e-14 ,np.sqrt(beta*(va-r90)/(va*(beta-r90))), vb)
        """
        ind_vb_le = np.where(va*(beta-r90)<=1e-14)
        ind_vb_gt = np.where(va*(beta-r90)>1e-14)
        vb[ind_vb_le]=np.sqrt(beta*(va-r90)/(1e-14))
        vb[ind_vb_gt]=np.sqrt(beta*(va-r90)/(va*(beta-r90)))
        """
        vbNN = vb**(N-1)
        vbNNinv = 1/vbNN
        vainv = 1/va
        s1=ta*t90*(vbNN-vbNNinv)
        s2=ta*(va-vainv)
        s3=va*vbNN-vainv*vbNNinv-r90*(vbNN-vbNNinv)

        RN=ra+s1/s3
        TN=s2/s3
        LRT = np.zeros((self.nlambd, 3))
        LRT[:,0] = lambd
        LRT[:,1] = RN
        LRT[:,2] = TN

        return LRT

# Jacquemoud S., Ustin S.L., Verdebout J., Schmuck G., Andreoli G.,
# Hosgood B. (1996), Estimating leaf biochemistry using the PROSPECT
# leaf optical properties model, Remote Sens. Environ., 56:194-202.

# Jacquemoud S., Baret F. (1990), PROSPECT: a model of leaf optical
# properties spectra, Remote Sens. Environ., 34:75-91.

# Feret et al. (2008), PROSPECT-4 and 5: Advances in the Leaf Optical
# Properties Model Separating Photosynthetic Pigments, Remote Sensing of

# Allen W.A., Gausman H.W., Richardson A.J., Thomas J.R. (1969),
# Interaction of isotropic ligth with a compact plant leaf, J. Opt.
# Soc. Am., 59(10):1376-1379.

# Stokes G.G. (1862), On the intensity of the light reflected from
# or transmitted through a pile of plates, Proc. Roy. Soc. Lond.,
# 11:545-556.


