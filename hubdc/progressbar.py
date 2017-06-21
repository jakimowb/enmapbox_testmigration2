from __future__ import print_function

class CUIProgress(object):

    def __init__(self):
        self.totalsteps = 100

    def setTotalSteps(self, steps):
        self.totalsteps = steps

    def setProgress(self, progress):
        progress = int(float(progress) / self.totalsteps * 100)
        if progress == self.totalsteps:
            print('100%')
        else:
            print('{}%..'.format(progress), end='')

    def setLabelText(self,text):
        print('\n{}%..'.format(text))

    def displayWarning(self,text):
        print('Warning: {}'.format(text))

    def displayError(self,text):
        print('Error: {}'.format(text))

    def displayInfo(self,text):
        print('Info: {}'.format(text))

class SilentProgress(object):
    def __init__(self): pass
    def setTotalSteps(self, steps): pass
    def setProgress(self, progress): pass
    def setLabelText(self,text): pass
    def displayWarning(self,text): pass
    def displayError(self,text): pass
    def displayInfo(self,text): pass
