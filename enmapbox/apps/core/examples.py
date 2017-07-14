from enmapbox.apps.core.flowprovider import Image, Classification, Vector, Classifier, ProbabilitySample, ClassificationSample

imageFilename = r'C:\Work\data\EnMAPUrbanGradient2009\01_image_products\EnMAP01_Berlin_Urban_Gradient_2009.bsq'
vectorFilename=r'C:\Work\data\EnMAPUrbanGradient2009\02_additional_data\land_cover\LandCov_Vec_Berlin_Urban_Gradient_2009.shp'
classification3mFilename = r'c:\output\classification3m.img'
probabilitySample30mFilename = r'c:\output\probabilitySample30m.img'
classificationSample30mFilename = r'c:\output\classificationSample30m.img'
classifierFilename = r'c:\output\classifier.img'

def vector_classify():
    image = Image(filename=imageFilename)
    vector = Vector(filename=vectorFilename)
    classification = vector.classify(filename=classification3mFilename,
                                     pixelGrid=image.pixelGrid.newResolution(xRes=3, yRes=3),
                                     ids=[1,2,3,4,5,6], idAttribute='ID_L2',
                                     classNames=['Roof',  'Pavement',   'Grass',   'Tree',   'Soil',    'Other'],
                                     classLookup=[168,0,0, 156,156,156,  151,229,0, 35,114,0, 136,89,67, 236,214,0])

def image_sampleByClassification():
    image = Image(filename=imageFilename)
    classification = Classification(filename=classification3mFilename)
    probabilitySample = image.sampleByClassification(classification=classification)
    probabilitySample.pickle(filename=probabilitySample30mFilename)

def probabilitySample_classify():
    probabilitySample = ProbabilitySample.unpickle(filename=probabilitySample30mFilename)
    classificationSample = probabilitySample.classify(minOverallCoverage=0.75, minWinnerCoverage=0.5)
    classificationSample.pickle(filename=classificationSample30mFilename)

def classifier_fit():
    from sklearn.ensemble import RandomForestClassifier
    classificationSample = ClassificationSample.unpickle(filename=classificationSample30mFilename)
    classifier = Classifier(sklClassifier=RandomForestClassifier())
    classifier.fit(sample=classificationSample)
    classifier.pickle(filename=classifierFilename)

def classifier_predictImage():
    classifier = Classifier.unpickle(filename=classifierFilename)
    classification = classifier.predictImage()




if __name__ == '__main__':
    #vector_classify()
    #image_sampleByClassification()
    probabilitySample_classify()
    classifier_fit()
