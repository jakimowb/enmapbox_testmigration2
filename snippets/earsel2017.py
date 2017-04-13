from enmapbox.processing.types import *
from enmapbox.processing.estimators import *
import numpy as np

def readOnly():
    import processing
    img = Image('<path spectral image>')
    cal = Classification('<path calibration labels>')
    val = Classification('<path validation labels>')

    rfc = RandomForestClassifier()
    rfc.fit(img, cal)
    map = rfc.predict(img)
    accAssReport = map.assessClassificationPerformance(val)
    accAssReport.report().saveHTML('<path report file>')



def ufunc():
    # generate result arrays
    ysize = 500
    xsize = 500
    nbands = 50
    nfiles = 50
    arrays = list()
    for i in range(nfiles):
        array = np.random.rand(nbands, ysize, xsize) * 42
        arrays.append(array.astype(numpy.int16))
    return arrays

def callbackTest():

    t0 = np.datetime64('now')

    def checkpoint(msg):
        global t0
        dt = np.datetime64('now')-t0
        print('{}:{}'.format(msg, dt))
        t0 = np.datetime64('now')

    checkpoint('Start')
    #def single-time ufunc

if __name__ == '__main__':
    callbackTest()

