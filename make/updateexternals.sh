#!/bin/bash

#run the "git remote add <...repository...>" line if the repository
#has not been added as remote repository

#update pyqtgraph
git remote add pyqtgraph https://github.com/pyqtgraph/pyqtgraph.git
git fetch pyqtgraph
git read-tree --prefix=site-packages/pyqtgraph -u pyqtgraph/master
git commit -m "updated pyqtgraph"

#update hub-datacube
git remote add hub-datacube https://bitbucket.org/hu-geomatics/hub-datacube.git
git fetch hub-datacube
git read-tree --prefix=site-packages/hubdc -u hub-datacube/master:hubdc
git commit -m "updated hub-datacube"

#update hub-workflow
git remote add hub-workflow https://bitbucket.org/hu-geomatics/hub-workflow.git
git fetch hub-workflow
git read-tree --prefix=site-packages/hubflow -u hub-workflow/master:hubflow
git commit -m "updated hub-workflow"




