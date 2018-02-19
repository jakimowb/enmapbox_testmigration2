from __future__ import print_function
import sys

class ProgressBar(object):
    def setPercentage(self, percentage): pass
    def setText(self, text): pass

class SilentProgressBar(ProgressBar):
    pass

class CUIProgressBar(ProgressBar):

    def setPercentage(self, percentage):
        percentage = int(percentage)
        if percentage == 100:
            print('100%')
        else:
            print('{}%..'.format(percentage), end='')
        sys.stdout.flush()

    def setText(self, text):
        print(text)
        sys.stdout.flush()
