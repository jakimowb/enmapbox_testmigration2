.. _Open Test Maps:

**************
Open Test Maps
**************

Opens testdata into current QGIS project (LandCov_BerlinUrbanGradient.shp, HighResolution_BerlinUrbanGradient.bsq, EnMAP_BerlinUrbanGradient.bsq, SpecLib_BerlinUrbanGradient.sli).

**Parameters**

**Outputs**


:guilabel:`EnMAP (30m; 177 bands)` [rasterDestination]
    File name: EnMAP_BerlinUrbanGradient.bsq
    
    Simulated EnMAP data (based on 3.6m HyMap imagery) acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). It has a spectral resolution of 177 bands and a spatial resolution of 30m.


:guilabel:`HyMap (3.6m; Blue, Green, Red, NIR bands)` [rasterDestination]
    File name: HighResolution_BerlinUrbanGradient.bsq
    
    HyMap image acquired in August 2009 over south eastern part of Berlin covering an area of 4.32 km^2 (2.4 x 1.8 km). This dataset was reduced to 4 bands (0.483, 0.558, 0.646 and 0.804 micrometers). The spatial resolution is 3.6m.


:guilabel:`LandCover Layer` [vectorDestination]
    File name: LandCov_BerlinUrbanGradient.shp
    
    Polygon shapefile containing land cover information on two classification levels. Derived from very high resolution aerial imagery and cadastral datasets.
    
    Level 1 classes: Impervious; Other; Vegetation; Soil
    
    Level 2 classes: Roof; Low vegetation; Other; Pavement; Tree; Soil

