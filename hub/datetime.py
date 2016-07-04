from __future__ import absolute_import
import datetime
import calendar

class Date(datetime.date):

    @property
    def doy(self):
        return (self - datetime.date(self.year, 1, 1)).days +1


    def decimalYear(self):
        return self.year + self.doy/(365.+calendar.isleap(self.year))


if __name__ == '__main__':

    date = Date(2000,7,1)
    print date.decimalYear()