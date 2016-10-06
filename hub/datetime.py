from __future__ import absolute_import
import datetime
import calendar

class Date(datetime.date):

    @staticmethod
    def fromYearDoy(year, doy):
        date = datetime.date(year=year, month=1, day=1) + datetime.timedelta(days=doy-1)
        return Date(year=date.year, month=date.month, day=date.day)


    @staticmethod
    def fromText(text):
        # text format: yyyy-mm-dd
        return Date(year=int(text[0:4]), month=int(text[5:7]), day=int(text[8:10]))


    @property
    def doy(self):
        return (self - datetime.date(self.year, 1, 1)).days +1

    @property
    def decimalYear(self):
        return self.year + self.doy/(365.+calendar.isleap(self.year))


if __name__ == '__main__':

    date = Date(2000,7,1)
