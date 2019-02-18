# -*- coding: utf-8 -*-

"""
***************************************************************************
    exampleapp/algorithms.py

    Some example algorithms, as they might be implemented somewhere else
    ---------------------
    Date                 : Juli 2017
    Copyright            : (C) 2017 by Benjamin Jakimow
    Email                : benjamin.jakimow@geo.hu-berlin.de
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import time
import gdalnumeric
import os
from engeomap import APP_DIR
from engeomap import engeomap_aux_func as auxfun
from PyQt5 import QtGui


def thresholder(guidat):
    try:
        guidat = guidat.strip()
        guidat = float(guidat)
    except(Exception):
        print("Error only float values between 0] and [1 allowed")
        return None
    if (guidat > 0) and (guidat < 1):
        pass
    else:
        print("Error only float values between 0] and [1 allowed")
        return None
    return guidat


def thresholder2(guidat):
    try:
        guidat = guidat.strip()
        guidat = int(guidat)
    except(Exception):
        print("Error only float values between 0] and [1 allowed")
        return None
    if (guidat > 1):
        pass
    else:
        print("Error only int values ge 1 allowed")
        return None
    return guidat


def brp(path):
    if '.' in path:
        hdr = path.split('.')[0]+".hdr"
    else:
        hdr = path.strip()+".hdr"
    return path.strip(), hdr


"""
def sensorbuhl(buhle):
    if float(buhle) == 1:
        sensor = 'enmap'
    else:
        sensor = "hyperion"
    return sensor"""


def engeomapp_headless(params):
    # Parameter:
    print('Hallo')
    print(params['vnirt'])
    print(params['swirt'])
    print(params['fit_thresh'])
    print(params['mixminerals'])
    # print(params['enmap'])
    # print(params['hyperion'])
    print(params['laboratory'])
    print(params['liblab'])
    print(params['image'])
    print(params['library'])
    print(params['farbe'])
    vnirt = thresholder(params['vnirt'])
    swirt = thresholder(params['swirt'])
    fit_thr = thresholder(params['fit_thresh'])
    mix_minerals = thresholder2(params['mixminerals'])
    imasch = brp(params['image'])#[0]==data [1]==header
    lib = brp(params['library'])
    farb = brp(params['farbe'])
    #sensor = sensorbuhl(params['enmap'])
    liblab = float(params['liblab'])
    lab = float(params['laboratory'])
    ###################################

#def mapper_fullrange(bildname,libname,colorfile):
def mapper_fullrange(params):
    bildname=params['image']
    libname=(params['library'])
    colorfile=params['farbe']
    vnir_thr=thresholder(params['vnirt'])
    swir_thr=thresholder(params['swirt'])
    mix_minerals=thresholder2(params['mixminerals'])
    fit_threshold=thresholder(params['fit_thresh'])
    basename=bildname.split('.')[0]
    wbild,w1nmbild,bilddata=auxfun.check_load_data(bildname)
    wlib,w1nmlib,libdata=auxfun.check_load_data(libname)
    lsh=libdata.shape
    bsh=bilddata.shape
    minn,maxx,minflag,maxflag=auxfun.compare_wavelengths(w1nmlib,w1nmbild)
    interpol_wvls=auxfun.prep_1nm_interpol_intersect(minn,maxx,minflag,maxflag,w1nmlib,w1nmbild)
    cvxabs_mod,cvxrel_mod,libdat_rel_weighted,libdat_rel_chm_weighted,vnirmax,swirmax=auxfun.treat_library_cvx_full_range(wlib,libdata,interpol_wvls,vnir_thr=0.01,swir_thr=0.01)
    correlat,bvlss,bvlserr,vnirposmat,vnirdepthmat,swirposmat,swirdepthmat=auxfun.fitting_cvx_fullrange(wbild,interpol_wvls,bilddata,libdat_rel_weighted,libdat_rel_chm_weighted,cvxabs_mod,vnir_thr=0.01,swir_thr=0.01,lib_flag=0,mix_minerals=10,fit_threshold=0.2)
    auxfun.reshreib(correlat,basename+'_correlation_result',[lsh[0],bsh[1],bsh[2]])
    auxfun.reshreib(bvlss,basename+'_unmix_result',[lsh[0],bsh[1],bsh[2]])
    auxfun.reshreib2d(bvlserr,basename+'_unmix_error',[bsh[1],bsh[2]])
    rgbdurchschn,rgbdurchschn2,indexmatdurchschn,rgbmdurchschn,rgbm2durschschn=auxfun.corr_colours(correlat,colorfile,basename+'_bestmatches_correlation_',[lsh[0],bsh[1],bsh[2]],minerals=lsh[0])
    rgbu,rgbu1,indexmatu,rgbum,rgbum2=auxfun.corr_colours_unmix(bvlss,colorfile,basename+'_bestmatches_correlation_',[lsh[0],bsh[1],bsh[2]],minerals=lsh[0])
    auxfun.reshreib2d(vnirposmat,basename+'_vnirpos_of_max_abs',[bsh[1],bsh[2]])
    auxfun.reshreib2d(swirposmat,basename+'_swirpos_of_max_abs',[bsh[1],bsh[2]])
    auxfun.reshreib2d(vnirdepthmat,basename+'_vnirdepth_of_max_abs',[bsh[1],bsh[2]])
    auxfun.reshreib2d(swirdepthmat,basename+'_swirdepth_of_max_abs',[bsh[1],bsh[2]])
    return None
    
