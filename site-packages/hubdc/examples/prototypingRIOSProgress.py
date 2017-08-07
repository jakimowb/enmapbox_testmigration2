raster = r'C:\Work\data\EnMAPUrbanGradient2009\01_image_products\EnMAP01_Berlin_Urban_Gradient_2009.bsq'

from rios import applier

import sys
class ProgressBar(object):

    def __init__(self):
        self.totalsteps = 100

    def setTotalSteps(self, steps):
        self.totalsteps = steps

    def setProgress(self, progress):
        progress = int(float(progress) / self.totalsteps * 100)
        sys.stdout.write('%d%%\r' % progress)
        print('%d%%\r' % progress)

    def reset(self):
        sys.stdout.write('\n')

    def setLabelText(self,text):
        sys.stdout.write('\n%s\n' % text)

    def wasCancelled(self):
        return False

    def displayException(self,trace):
        sys.stdout.write(trace)

    def displayWarning(self,text):
        sys.stdout.write("Warning: %s\n" % text)

    def displayError(self,text):
        sys.stdout.write("Error: %s\n" % text)

    def displayInfo(self,text):
        sys.stdout.write("Info: %s\n" % text)

infiles = applier.FilenameAssociations()
infiles.image2 = raster
outfiles = applier.FilenameAssociations()

def idle(info, inputs, outputs): pass

controls = applier.ApplierControls()
controls.setProgress(ProgressBar())
applier.apply(idle, infiles, outfiles, controls=controls)

