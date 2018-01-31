1.
# before committing make sure to delete all outputs from hub-datacube/doc/source/DataModelExamples.ipynb
cd hub-datacube/doc/source
jupytor notebook DataModelExamples.ipynb
# select "Kernel -> Restart & Clear Output"
# save and close notebook

2.
# build an RST file from the notebook
jupytor nbconvert --to rst DataModelExamples.ipynb
