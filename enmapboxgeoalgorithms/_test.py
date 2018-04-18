

def test_Testdata():
    io = {'enmap': '', 'hymap': '', 'landcover': '', 'speclib': ''}
    runalg(OpenTestdata(), io)

    io = {'enmap': '', 'landcover': '', 'speclib': ''}
    runalg(OpenTestdataFull(), io)

    io = {'classification': join(outdir, 'CreateAdditionalTestdataClassification.img'),
          'probability': join(outdir, 'CreateAdditionalTestdataProbability.img'),
          'unsupervisedSample': join(outdir, 'CreateAdditionalTestdataUnsupervisedSample.img'),
          'classificationSample': join(outdir, 'CreateAdditionalTestdataClassificationSample.img'),
          'probabilitySample': join(outdir, 'CreateAdditionalTestdataProbabilitySample.img'),
          'regressionSample': join(outdir, 'CreateAdditionalTestdataRegressionSample.img')}
    runalg(CreateAdditionalTestdata(), io)

def test_generateRST():
    # generate GeoAlgorithms RST files
    generateRST()

