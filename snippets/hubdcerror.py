#see https://bitbucket.org/hu-geomatics/enmap-box/issues/134/valueerror-found-array-with-0-sample-s

pathClassifier = r'O:\Student_Data\Dierkes\5. Semester\Kretastudie\Bachelor arbeit\Classification\Classification_brandnew\classifier.pkl'
pathImage = r'O:\Student_Data\Dierkes\5. Semester\Kretastudie\Bachelor arbeit\Classification\Classification_brandnew\phenology_2016_testBJ.vrt'
pathDst = r'F:\Temp\Henrike\class.tif'


import pickle
import hubflow.core
from hubflow.core import FlowObject, Classifier, Estimator, Raster, ApplierOutputRaster, Applier

f = open(pathClassifier, 'rb')
classifier = pickle.load(file=f)
f.close()
assert isinstance(classifier, Classifier)
blockSize=hubflow.core.Size(1024,1024)
classifier.predict(filename=pathDst, raster=Raster(filename=pathImage), blockSize=blockSize)