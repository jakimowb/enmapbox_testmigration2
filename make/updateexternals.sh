#!/bin/bash

#run the "git remote add <...repository...>" line if the repository
#has not been added as remote repository

#update pyqtgraph
a=$(git ls-remote --exit-code pyqtgraph | grep pyqtgraph)
if $("$a" = ""); then
    git remote add pyqtgraph https://github.com/pyqtgraph/pyqtgraph.git
    git fetch pyqtgraph
    git read-tree --prefix=site-packages/pyqtgraph -u pyqtgraph/master
fi




a=$(git ls-remote --exit-code spectralpython | grep spectralpython)
if $("$a" = ""); then
    git remote add spy https://github.com/spectralpython/spectral.git
    git fetch spy
    git read-tree --prefix=site-packages/spy -u spy/master
else
    git fetch spy
    git read-tree --prefix=site-packages/spy -u spy/master
fi


a=$(git ls-remote --exit-code geoalgs | grep geoalgs)
if $("$a" = ""); then
    git remote add geoalgs https://@bitbucket.org/hu-geomatics/enmap-box-geoalgorithmsprovider.git
    git fetch geoalgs
    git read-tree --prefix=enmapboxgeoalgorithms/ -u geoalgs/master:enmapboxgeoalgorithms
else
    git fetch geoalgs
    git read-tree --prefix=enmapbox/geoalgorithms/ -u geoalgs/master:enmapboxgeoalgorithms
fi

#git commit -m "updated pyqtgraph"

#update hub-datacube
a=$(git ls-remote --exit-code hub-datacube | grep hub-datacube)
if $("$a" = ""); then
    git remote add hub-datacube https://bitbucket.org/hu-geomatics/hub-datacube.git
fi

git fetch hub-datacube
git read-tree --prefix=site-packages/hubdc -u hub-datacube/master:hubdc
#git commit -m "updated hub-datacube"

#update hub-workflow
a=$(git ls-remote --exit-code hub-workflow | grep hub-workflow)
if $("$a" = ""); then
    git remote add hub-datacube https://bitbucket.org/hu-geomatics/hub-workflow.git
fi
git fetch hub-workflow
git read-tree --prefix=site-packages/hubflow -u hub-workflow/master:hubflow
#git commit -m "updated hub-workflow"




