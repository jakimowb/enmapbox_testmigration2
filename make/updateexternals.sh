#!/bin/bash

#run the "git remote add <...repository...>" line if the repository
#has not been added as remote repository

#update pyqtgraph
a=$(git ls-remote --exit-code pyqtgraph | grep pyqtgraph)
if $("$a" = ""); then
    git remote add pyqtgraph https://github.com/pyqtgraph/pyqtgraph.git
fi

git fetch pyqtgraph
git read-tree --prefix=site-packages/pyqtgraph -u pyqtgraph/master
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




