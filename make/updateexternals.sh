#!/bin/bash

#run the "git remote add <...repository...>" line if the repository
#has not been added as remote repository

#update pyqtgraph
a=$(git ls-remote --exit-code pyqtgraph | grep pyqtgraph)
if $("$a" = ""); then
    git remote add pyqtgraph https://github.com/pyqtgraph/pyqtgraph.git
fi
git rm -rf site-packages/pyqtgraph
git fetch pyqtgraph
git read-tree --prefix=site-packages/pyqtgraph -u pyqtgraph/master
git commit -m "updated pyqtgraph from remote repository"


#update enmapbox-testdata
a=$(git ls-remote --exit-code enmapboxtestdata | grep enmapboxtestdata)
if $("$a" = ""); then
    git remote add enmapboxtestdata https://jakimowb@bitbucket.org/hu-geomatics/enmap-box-testdata.git
fi
git rm -rf enmapboxtestdata
git fetch enmapboxtestdata
git read-tree --prefix=enmapboxtestdata -u enmapboxtestdata/master:enmapboxtestdata
git commit -m "updated enmapboxtestdata from remote repository"


a=$(git ls-remote --exit-code spectralpython | grep spectralpython)
if $("$a" = ""); then
    git remote add spy https://github.com/spectralpython/spectral.git
fi
git rm -rf site-packages/spy
git fetch spy
git read-tree --prefix=site-packages/spy -u spy/master
git commit -m "updated Spectra Python (SPy) from remote repository"

a=$(git ls-remote --exit-code geoalgs | grep geoalgs)
if $("$a" = ""); then
    git remote add geoalgs https://@bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git
fi
git rm -rf enmapboxgeoalgorithms
git fetch geoalgs
git read-tree --prefix=enmapboxgeoalgorithms/ -u geoalgs/master:enmapboxgeoalgorithms
git commit -m "updated enmapboxgeoalgorithms from remote repository"

#update hub-datacube
a=$(git ls-remote --exit-code hub-datacube | grep hub-datacube)
if $("$a" = ""); then
    git remote add hub-datacube https://bitbucket.org/hu-geomatics/hub-datacube.git
fi
git rm -rf site-packages/hubdc
git fetch hub-datacube
git read-tree --prefix=site-packages/hubdc -u hub-datacube/master:hubdc
git commit -m "updated hub-datacube from remote repository"


#update hub-workflow
a=$(git ls-remote --exit-code hub-workflow | grep hub-workflow)
if $("$a" = ""); then
    git remote add hub-workflow https://bitbucket.org/hu-geomatics/hub-workflow.git
fi
git rm -rf site-packages/hubflow
git fetch hub-workflow
git read-tree --prefix=site-packages/hubflow -u hub-workflow/master:hubflow
git commit -m "updated hub-workflow from remote repository"




