============
Installation
============

pip install
===========

The following dependencies must be available: *gdal*, *matplotlib* (optional)

Install the latest released version::

    python -m pip install https://bitbucket.org/hu-geomatics/hub-datacube/get/master.tar.gz

Or install the latest developer version::

    python -m pip install https://bitbucket.org/hu-geomatics/hub-datacube/get/develop.tar.gz

conda install
=============

Create a stand-alone Python environment with conda::

    conda config --add channels conda-forge
    conda create -n hubenv gdal matplotlib
    activate hubenv

Install the latest released or developer version with pip (see **pip install** section above).
