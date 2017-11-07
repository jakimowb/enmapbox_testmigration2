from __future__ import print_function
import sys

class ProgressBar(object):
    def __init__(self):
        self.totalsteps = 100
        self.percentage = 0.
    def setTotalSteps(self, steps):
        self.totalsteps = steps
    def setProgress(self, progress):
        self.percentage = float(progress) / self.totalsteps * 100
    def setLabelText(self, text): pass
    def displayWarning(self, text): pass
    def displayError(self, text): pass
    def displayInfo(self, text, type): pass

class SilentProgressBar(ProgressBar):
    pass

class CUIProgressBar(ProgressBar):

    def setProgress(self, progress):
        ProgressBar.setProgress(self, progress=progress)
        percentage = int(self.percentage)
        if percentage == 100:
            print('100%')
        else:
            print('{}%..'.format(percentage), end='')
        sys.stdout.flush()

    def setLabelText(self, text):
        print(text)
        sys.stdout.flush()

    def displayWarning(self,text):
        print('Warning: {}'.format(text))
        sys.stdout.flush()

    def displayError(self,text):
        print('Error: {}'.format(text))
        sys.stdout.flush()

    def displayInfo(self,text, type=''):
        print('{}Info: {}'.format(type, text))
        sys.stdout.flush()

try:
    from processing.core.SilentProgress import SilentProgress as SP
    from processing.gui.AlgorithmDialogBase import AlgorithmDialogBase as ADB
except:
    SP = type(None)
    ADB = type(None)

class ProgressBarDelegate(ProgressBar):

    def __init__(self, progressBar):
        self.totalsteps = 100
        self.percentage = 0.
        self.progressBar = progressBar
        self.isQgis = isinstance(progressBar, (SP, ADB))

    def setTotalSteps(self, steps):
        if self.isQgis: ProgressBar.setTotalSteps(self, steps=steps)
        else: self.progressBar.setTotalSteps(steps=steps)

    def setProgress(self, progress):
        if self.isQgis:
            ProgressBar.setProgress(self, progress=progress)
            self.setPercentage(self.percentage)
        else:
            self.progressBar.setProgress(progress=progress)

    def setLabelText(self, text):
        if self.isQgis: self.progressBar.setText(text)
        else: self.progressBar.setLabelText(text=text)

    def displayWarning(self, text):
        self.progressBar.displayWarning(text=text)

    def displayError(self, text):
        self.progressBar.displayError(text=text)

    def displayInfo(self, text, type):
        self.progressBar.displayInfo(text=text, type=type)

    def setText(self, text):
        self.progressBar.setLabelText(text)

    def setPercentage(self, i):
        self.progressBar.setPercentage(i)

    def setInfo(self, msg):
        self.progressBar.displayInfo(msg)

    def setCommand(self, msg):
        self.progressBar.setLabelText(msg)

    def setDebugInfo(self, msg):
        self.progressBar.displayInfo(msg, type='DEBUG ')

    def setConsoleInfo(self, msg):
        self.progressBar.displayInfo(msg, type='CONSOLE ')

    def close(self):
        pass

