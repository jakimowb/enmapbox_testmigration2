# -*- coding: utf-8 -*-

from dataSpec import *
from SAILdata import *
import numpy as np
import time
from math import pi, radians, sin, cos, tan, sqrt, exp, log, asin, acos

class Sail:

    def __init__(self, tts, tto, psi):

        self.tts = tts
        self.tto = tto
        self.psi = psi

        self.sintts = sin(tts)
        self.sintto = sin(tto)
        self.costts = cos(tts)
        self.costto = cos(tto)
        self.cospsi = cos(psi)


    def Pro4sail(self, rho, tau, LIDF, TypeLIDF, LAI, hspot, psoil):

        costts_costto = self.costts*self.costto
        tantts = tan(self.tts)
        tantto = tan(self.tto)
        dso = sqrt(tantts**2 + tantto**2 - 2*tantts*tantto*self.cospsi)

        # Soil Reflectance Properties
        rsoil = psoil*Rsoil1+(1-psoil)*Rsoil2

        # Generate Leaf Angle Distribution From Average Leaf Angle (ellipsoidal) or (a,b) parameters
        lidf = self.LIDF_calc(LIDF, TypeLIDF)

        # Weighted Sums of LIDF
        na = 13
        litab = np.concatenate((np.arange(5,85,10), np.arange(81,91,2)),axis=0) # 5, 15, 25, 35, 45, ... , 75, 81, 83, ... 89
        litab = np.radians(litab)

        # Initialize angular distances
        ks, ko, bf, sob, sof = 0.0, 0.0, 0.0, 0.0, 0.0

        # debug:
        koli_temp = []
        chi_o_temp = []

        for i in xrange(na):
            ttl = litab[i] # leaf inclination discrete values
            chi_s, chi_o, frho, ftau = self.volscatt(ttl)

            # Extinction coefficients
            ksli = chi_s/self.costts
            koli = chi_o/self.costto
            
            # debug            
            koli_temp.append(koli)
            chi_o_temp.append(chi_o)

            # Area scattering coefficient fractions
            sobli = frho * pi/costts_costto
            sofli = ftau * pi/costts_costto
            bfli = cos(ttl)**2
            ks += ksli * lidf[i]
            ko += koli * lidf[i]
            bf += bfli * lidf[i]
            sob += sobli * lidf[i]
            sof += sofli * lidf[i]

        # Geometric factors to be used later with reflectance and transmission
        sdb = 0.5 * (ks + bf)
        sdf = 0.5 * (ks - bf)
        dob = 0.5 * (ko + bf)
        dof = 0.5 * (ko - bf)
        ddb = 0.5 * (1 + bf)
        ddf = 0.5 * (1 - bf)

        # Refl and Transm kick in
        sigb = ddb*rho + ddf*tau
        sigf = ddf*rho + ddb*tau
        att = 1.0-sigf
        m2 = (att + sigb) * (att - sigb)
        m2[m2<=0] = 0.0
        m = np.sqrt(m2)

        sb = sdb*rho + sdf*tau
        sf = sdf*rho + sdb*tau
        vb = dob*rho + dof*tau
        vf = dof*rho + dob*tau
        w = sob*rho + sof*tau

        # Include LAI (make sure, LAI is > 0!)
        e1 = np.exp(-m*LAI)
        e2 = e1**2
        rinf = (att-m) / sigb
        rinf2 = rinf**2
        re = rinf*e1
        denom = 1.0 - rinf2 * e2

        J1ks = self.Jfunc1(ks, m, LAI)
        J2ks = self.Jfunc2(ks, m, LAI)
        J1ko = self.Jfunc1(ko, m, LAI)
        J2ko = self.Jfunc2(ko, m, LAI)

        Ps = (sf + sb*rinf) * J1ks
        Qs = (sf*rinf + sb) * J2ks
        Pv = (vf + vb*rinf) * J1ko
        Qv = (vf*rinf + vb) * J2ko

        rdd = rinf*(1.0 - e2)/denom
        tdd = (1.0 - rinf2) * e1/denom
        tsd = (Ps - re*Qs)/denom
        rsd = (Qs - re*Ps)/denom
        tdo = (Pv - re*Qv)/denom
        rdo = (Qv - re*Pv)/denom

        tss = exp(-ks * LAI)
        too = exp(-ko * LAI)
        z = self.Jfunc2(ks, ko, LAI)
        g1 = (z - J1ks*too) / (ko + m)
        g2 = (z - J1ko*tss) / (ks + m)

        Tv1 = (vf*rinf + vb) * g1
        Tv2 = (vf + vb*rinf) * g2
        T1 = Tv1 * (sf + sb*rinf)
        T2 = Tv2 * (sf*rinf + sb)
        T3 = (rdo*Qs + tdo*Ps)*rinf

        # Multiple Scattering contribution to BRDF of canopy
        rsod = (T1 + T2 - T3) / (1.0 + rinf2)

        # Hotspot-effect
        alf = 200
        if hspot > 0: alf = (dso/hspot) * 2.0 / (ks + ko)
        if alf > 200: alf = 200
        if alf == 0: # pure hotspot, no shadow
            tsstoo = tss
            sumint = (1.0 - tss) / (ks * LAI)
        else: # Outside hotspot
            x1, y1, sumint, f1 = 0.0, 0.0, 0.0, 1.0
            try:
                fhot = LAI * sqrt(ko*ks)
            except:
                return [None]*len(lambd)

            fint = (1-exp(-alf))*0.05

            for i in xrange(19):
                if i<18:
                    x2 = -log(1.0 - (i+1)*fint)/alf
                else:
                    x2 = 1.0
                y2 = -(ko+ks)*LAI*x2 + fhot*(1.0-exp(-alf*x2))/alf
                f2 = exp(y2)
                sumint += (f2-f1)*(x2-x1)/(y2-y1)
                x1 = x2
                y1 = y2
                f1 = f2

            tsstoo = f1

        # Bidirectional reflectance
        rsos = w * LAI * sumint # Single scattering contribution
        dn = 1.0 - rsoil * rdd # Soil interaction
        tdd_dn = tdd/dn
        rddt = rdd + tdd*rsoil*tdd_dn # bi-hemispherical reflectance factor
        rsdt = rsd + (tsd+tss)*rsoil*tdd_dn # directional-hemispherical reflectance factor for solar incident flux
        rdot = rdo + rsoil*(tdo+too)*tdd_dn # hemispherical-directional reflectance factor in viewing directino
        rsodt = rsod + ((tss+tsd)*tdo + (tsd + tss*rsoil*rdd)*too)*rsoil/dn
        rsost = rsos + tsstoo*rsoil
        rsot = rsost + rsodt # rsot: bi-directional reflectance factor

        # Direct/diffuse light
        sin_90tts = sin(pi/2 - self.tts)
        skyl = 0.847 - 1.61*sin_90tts + 1.04*sin_90tts**2
        PARdiro = (1.0-skyl)*Es
        PARdifo = skyl*Ed

        resv = (rdot*PARdifo + rsot*PARdiro) / (PARdiro + PARdifo)

        return resv

    def LIDF_calc(self, LIDF, TypeLIDF): # Calculates the Leaf Angle Distribution Function Value (freq)

        if TypeLIDF==1: # Beta-Distribution

            freq = beta_dict[LIDF] # look up frequencies for beta-distribution

        else: # Ellipsoidal distribution

            freq = self.campbell(LIDF)

        return freq

    def campbell(self, ALIA): # Calculates the Leaf Angle Distribution Function value (freq) Ellipsoidal distribution function from ALIA

        n = 13
        excent = exp(-1.6184e-5*ALIA**3 + 2.1145e-3*ALIA**2 - 1.2390e-1*ALIA + 3.2491)
        freq=[0.0]*n

        for i in xrange(n):
            if excent==1.0:
                freq[i] = abs(cos_tl1[i]-cos_tl2[i])
            else:
                x1 = excent/sqrt(1.0 + excent**2 * tan_tl1[i])
                x12 = x1**2
                x2 = excent/sqrt(1.0 + excent**2 * tan_tl2[i])
                x22 = x2**2
                alpha = excent / sqrt(abs(1-excent**2))
                alpha2 = alpha**2
                if excent > 1.0:
                    alpx1 = sqrt(alpha2+x12)
                    alpx2 = sqrt(alpha2+x22)
                    dum = x1*alpx1 + alpha2*log(x1+alpx1)
                    freq[i] = abs(dum-(x2*alpx2+alpha2*log(x2+alpx2)))
                else:
                    almx1 = sqrt(alpha2-x12)
                    almx2 = sqrt(alpha2-x22)
                    dum = x1*almx1+alpha2*asin(x1/alpha)
                    freq[i] = abs(dum-(x2*almx2+alpha2*asin(x2/alpha)))

        result = np.asarray(freq)/sum(freq)
        return result

    def volscatt(self, ttl):

        costtl = cos(ttl)
        sinttl = sin(ttl)
        cs = costtl * self.costts
        co = costtl * self.costto
        ss = sinttl * self.sintts
        so = sinttl * self.sintto

        if abs(ss) > 1e-6:
            cosbts = -cs/ss
        else:
            cosbts = 5.0

        if abs(so) > 1e-6:
            cosbto = -co/so
        else:
            cosbto = 5.0

        if abs(cosbts) < 1:
            bts = acos(cosbts)
            ds = ss
        else:
            bts = pi
            ds = cs

        chi_s = 2.0 / pi*((bts - pi*0.5)*cs + sin(bts)*ss)

        if abs(cosbto) < 1:
            bto = acos(cosbto) # hier werden bto < pi/2 erzeugt!
            doo = so
        elif self.tto < (pi*0.5): # wenn er hier landet ist alles ok
            bto = pi 
            doo = co
        else:
            bto = 0.0
            doo = -co

        # chi_o wird negativ, wenn bto < pi/2
        chi_o = 2.0 / pi*((bto - pi*0.5)*co + sin(bto)*so)

        btran1 = abs(bts-bto)
        btran2 = pi - abs(bts + bto - pi)

        if self.psi < btran1:
            bt1 = self.psi
            bt2 = btran1
            bt3 = btran2
        elif self.psi <= btran2:
            bt1 = btran1
            bt2 = self.psi
            bt3 = btran2
        else:
            bt1 = btran1
            bt2 = btran2
            bt3 = self.psi

        t1 = 2*cs*co + ss*so*self.cospsi

        if bt2 > 0:
            t2 = sin(bt2)*(2*ds*doo + ss*so*cos(bt1)*cos(bt3))
        else:
            t2 = 0

        denom = 2.0*pi**2
        frho = ((pi-bt2)*t1 + t2)/denom
        ftau = (-bt2*t1 + t2)/denom

        if frho < 0: frho = 0.0
        if ftau < 0: ftau = 0.0

        return chi_s, chi_o, frho, ftau

    def Jfunc1(self, k,l,t): # J1 function with avoidance of singularity problem

        Del = (k-l)*t
        Jout = [(exp(-l[i]*t)-exp(-k*t)) / (k-l[i])
                if abs(Del[i]) > 1e-3
                else 0.5 * t * (exp(-k*t)+exp(-l[i]*t)) * (1.0-Del[i]*Del[i]/12)
                for i in xrange(len(l))]
        return np.asarray(Jout)

    def Jfunc2(self, k,l,t):
        Jout = (1.0-np.exp(-(k+l)*t))/(k+l)
        return Jout