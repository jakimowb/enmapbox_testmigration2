# -*- coding: utf-8 -*-

"""
***************************************************************************
   algorithms.py

This is EnGeoMAP further information can be found in the following open acess publication:
Mielke, C.; Rogass, C.; Boesche, N.; Segl, K.; Altenberger, U. 
EnGeoMAP 2.0—Automated Hyperspectral Mineral Identification for the German EnMAP Space Mission. 
Remote Sens. 2016, 8, 127. 
    ---------------------
    Date                 : Juli 2019
    Copyright            : (C) 2019 by Christian Mielke
    Email                : christian.mielke@gfz-potsdam.de
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
import os,numpy
from engeomap import APP_DIR
from engeomap import engeomap_aux_funcul as auxfunul
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
    lib_flag = 0
    basename=bildname.split('.')[0]
    wbild,w1nmbild,bilddata=auxfunul.check_load_data(bildname)
    wlib,w1nmlib,libdata=auxfunul.check_load_data(libname)
    lsh=libdata.shape
    bsh=bilddata.shape
    minn,maxx,minflag,maxflag=auxfunul.compare_wavelengths(w1nmlib,w1nmbild)
    interpol_wvls=auxfunul.prep_1nm_interpol_intersect(minn,maxx,minflag,maxflag,w1nmlib,w1nmbild)
    cvxabs_mod, cvxrel_mod, libdat_rel_weighted, libdat_rel_chm_weighted, vnirmax, swirmax= auxfunul.treat_library_cvx_full_range(
        wlib, libdata, interpol_wvls, vnir_thr, swir_thr)
    correlat, bvlss, bvlserr, vnirposmat, vnirdepthmat, swirposmat, swirdepthmat, astsum, depthsum, flsum, allessum = auxfunul.fitting_cvx_fullrange(
        wbild, interpol_wvls, bilddata, libdat_rel_weighted, libdat_rel_chm_weighted, cvxabs_mod, vnir_thr,
        swir_thr, lib_flag, mix_minerals, fit_threshold)
    auxfunul.reshreib(correlat, basename + '_correlation_result', [lsh[0], bsh[1], bsh[2]])
    auxfunul.reshreib(bvlss, basename + '_abundance_result', [lsh[0], bsh[1], bsh[2]])
    auxfunul.reshreib2d(bvlserr, basename + '_abundance_residuals', [bsh[1], bsh[2]])
    rgbdurchschn, indexmatdurchschn, rgbmdurchschn = auxfunul.corr_colours(correlat,
                                                                                                         colorfile,
                                                                                                         basename + '_bestmatches_correlation_',
                                                                                                         [lsh[0],
                                                                                                          bsh[1],
                                                                                                          bsh[2]],
                                                                                                         minerals=lsh[
                                                                                                             0])
    rgbu, indexmatu, rgbum = auxfunul.corr_colours_unmix(bvlss, colorfile,
                                                                      basename + '_abundance_unmix_',
                                                                      [lsh[0], bsh[1], bsh[2]], minerals=lsh[0])
    auxfunul.reshreib2d(vnirposmat, basename + '_vnirpos_of_max_abs', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(swirposmat, basename + '_swirpos_of_max_abs', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(vnirdepthmat, basename + '_vnirdepth_of_max_abs', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(swirdepthmat, basename + '_swirdepth_of_max_abs', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(astsum, basename + '_cum_depth_div_by_width', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(flsum, basename + '_cum_peak_area', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(depthsum, basename + '_cum_depth', [bsh[1], bsh[2]])
    cont1 = numpy.sum(bilddata, axis=0) * numpy.reshape(depthsum, (bsh[1], bsh[2]))
    cont2 = numpy.sum(bilddata, axis=0) * numpy.reshape(flsum, (bsh[1], bsh[2]))
    auxfunul.schreibeBSQsingle(cont1, basename + '_albedo_ndepth_contrast')
    auxfunul.schreibeBSQsingle(cont2, basename + '_albedo_narea_contrast')
    auxfunul.rewrite_headers(basename + '.hdr')
    return None

#def mapper_fullrange(bildname,libname,colorfile):
def mapper_fullrange2(params):
    bildname = params['image']
    libname = (params['library'])
    colorfile = params['farbe']
    vnir_thr = thresholder(params['vnirt'])
    swir_thr = thresholder(params['swirt'])
    mix_minerals = thresholder2(params['mixminerals'])
    fit_threshold = thresholder(params['fit_thresh'])
    lib_flag=0
    basename=bildname.split('.')[0]
    wbild,w1nmbild,bilddata=auxfunul.check_load_data(bildname)
    wlib,w1nmlib,libdata=auxfunul.check_load_data(libname)
    lsh=libdata.shape
    bsh=bilddata.shape
    minn,maxx,minflag,maxflag=auxfunul.compare_wavelengths(w1nmlib,w1nmbild)
    interpol_wvls=auxfunul.prep_1nm_interpol_intersect(minn,maxx,minflag,maxflag,w1nmlib,w1nmbild)
    cvxabs_mod,cvxrel_mod,libdat_rel_weighted,libdat_rel_chm_weighted,vnirmax,swirmax=auxfunul.treat_library_cvx_full_range(wlib,libdata,interpol_wvls,vnir_thr,swir_thr)
    cvxabs_mod_alib,cvxrel_mod_alib,libdat_rel_weighted_alib,libdat_rel_chm_weighted_alib,vnirmax_alib,swirmax_alib=auxfunul.treat_library_cvx_full_range_lo(wlib, libdata, interpol_wvls, vnir_thr, swir_thr)
    correlat,bvlss,bvlserr,vnirposmat,vnirdepthmat,swirposmat,swirdepthmat,astsum,depthsum,flsum,allessum=auxfunul.fitting_cvx_fullrange(wbild,interpol_wvls,bilddata,libdat_rel_weighted,libdat_rel_chm_weighted,cvxabs_mod,vnir_thr,swir_thr,lib_flag,mix_minerals,fit_threshold)
    correlat_lo,bvlss_lo,bvlserr_lo,vnirposmat_lo,vnirdepthmat_lo,swirposmat_lo,swirdepthmat_lo,astsum_lo,depthsum_lo,flsum_lo,allessum_lo=auxfunul.fitting_cvx_fullrange_lo(wbild,interpol_wvls,bilddata,libdat_rel_weighted_alib,libdat_rel_chm_weighted_alib,cvxabs_mod_alib,vnir_thr,swir_thr,lib_flag,mix_minerals,fit_threshold)
    corravg=(correlat_lo+correlat)/2
    auxfunul.reshreib(correlat,basename+'_correlation_result',[lsh[0],bsh[1],bsh[2]])
    auxfunul.reshreib(correlat_lo, basename + '_correlation_result_peaks', [lsh[0], bsh[1], bsh[2]])
    auxfunul.reshreib(corravg, basename + '_correlation_result_average', [lsh[0], bsh[1], bsh[2]])
    auxfunul.reshreib(bvlss,basename+'_abundance_result',[lsh[0],bsh[1],bsh[2]])
    auxfunul.reshreib(bvlss_lo, basename + '_abndance_result_peaks', [lsh[0], bsh[1], bsh[2]])
    auxfunul.reshreib2d(bvlserr,basename+'_abndance_result_peaks_residuals',[bsh[1],bsh[2]])
    auxfunul.reshreib2d(bvlserr_lo, basename + '_unmix_error_peaks', [bsh[1], bsh[2]])
    rgbdurchschn,indexmatdurchschn,rgbmdurchschn=auxfunul.corr_colours(correlat,colorfile,basename+'_bestmatches_correlation_',[lsh[0],bsh[1],bsh[2]],minerals=lsh[0])
    rgbdurchschn, indexmatdurchschn, rgbmdurchschn = auxfunul.corr_colours(correlat_lo, colorfile,
                                                                  basename + '_bestmatches_correlation_peaks',
                                                                  [lsh[0], bsh[1], bsh[2]], minerals=lsh[0])
    rgbdurchschn, indexmatdurchschn, rgbmdurchschn = auxfunul.corr_colours(corravg, colorfile,
                                                                  basename + '_bestmatches_correlation_average',
                                                                  [lsh[0], bsh[1], bsh[2]], minerals=lsh[0])
    rgbu,indexmatu,rgbum=auxfunul.corr_colours_unmix(bvlss,colorfile,basename+'_bestmatches_abundance_',[lsh[0],bsh[1],bsh[2]],minerals=lsh[0])
    rgbu, indexmatu, rgbum =auxfunul.corr_colours_unmix(bvlss_lo, colorfile, basename + '_bestmatches_abundance_peaks',
                                                [lsh[0], bsh[1], bsh[2]], minerals=lsh[0])
    auxfunul.reshreib2d(vnirposmat,basename+'_vnirpos_of_max_abs',[bsh[1],bsh[2]])
    auxfunul.reshreib2d(swirposmat,basename+'_swirpos_of_max_abs',[bsh[1],bsh[2]])
    auxfunul.reshreib2d(vnirdepthmat,basename+'_vnirdepth_of_max_abs',[bsh[1],bsh[2]])
    auxfunul.reshreib2d(swirdepthmat,basename+'_swirdepth_of_max_abs',[bsh[1],bsh[2]])
    auxfunul.reshreib2d(astsum, basename + '_cum_depth_div_by_width', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(flsum, basename + '_cum_peak_area', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(depthsum, basename + '_cum_depth', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(vnirposmat_lo, basename + '_vnirpos_of_max_abs_peak', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(swirposmat_lo, basename + '_swirpos_of_max_abs_peak', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(vnirdepthmat_lo, basename + '_vnirdepth_of_max_abs_peak', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(swirdepthmat_lo, basename + '_swirdepth_of_max_abs_peak', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(astsum_lo, basename + '_cum_depth_div_by_width_peak', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(flsum_lo, basename + '_cum_peak_area_peak', [bsh[1], bsh[2]])
    auxfunul.reshreib2d(depthsum_lo, basename + '_cum_depth_peak', [bsh[1], bsh[2]])
    cont1=numpy.sum(bilddata,axis=0)*numpy.reshape(depthsum,(bsh[1],bsh[2]))
    cont2 =numpy.sum(bilddata,axis=0)*numpy.reshape(flsum,(bsh[1], bsh[2]))
    auxfunul.schreibeBSQsingle(cont1,basename +'_albedo_ndepth_contrast')
    auxfunul.schreibeBSQsingle(cont2,basename +'_albedo_narea_contrast')
    auxfunul.rewrite_headers(basename+'.hdr')
    return None
