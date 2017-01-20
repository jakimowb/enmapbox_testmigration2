from __future__ import absolute_import
import datetime as datetime_
import calendar

class Date(datetime_.date):

    @staticmethod
    def fromYearDoy(year, doy):
        date = datetime_.date(year=year, month=1, day=1) + datetime_.timedelta(days=doy-1)
        return Date(year=date.year, month=date.month, day=date.day)

    @staticmethod
    def fromText(text):
        # text format: yyyy-mm-dd or yyyymmdd
        yyyymmdd = text.replace('-', '')
        return Date(year=int(yyyymmdd[:4]), month=int(yyyymmdd[4:6]), day=int(yyyymmdd[6:]))

    @staticmethod
    def fromTimestamp(timestamp):
        # timestamp: the number of seconds since the epoch (see the time module)
        date = datetime_.datetime.fromtimestamp(timestamp)
        return Date(year=date.year, month=date.month, day=date.day)

    @staticmethod
    def fromLandsatSceneID(sceneID):
        # format e.g LE72240712013159CUB00
        return Date.fromYearDoy(year=int(sceneID[9:13]), doy=int(sceneID[13:16]))

    @staticmethod
    def fromSentinelSceneID(sceneID):
        # format e.g S2A_USER_PRD_MSIL2A_PDMC_20151224T192602_R065_V20151224T103329_20151224T103329.SAFE
        yyyymmdd = sceneID[47:55]
        return Date(year=int(yyyymmdd[:4]), month=int(yyyymmdd[4:6]), day=int(yyyymmdd[6:]))

    @property
    def doy(self):
        return (self - datetime_.date(self.year, 1, 1)).days +1

    @property
    def decimalYear(self):
        return self.year + self.doy/(365.+calendar.isleap(self.year))

class DateRange():

    def __init__(self, start=None, end=None):

        if start is not None:
            assert isinstance(start, Date)

        if start is not None:
            assert isinstance(end, Date)

        self.start = start
        self.end = end

    def inside(self, date):

        assert isinstance(date, Date)
        isInside = True
        if self.start is not None:
            isInside = isInside and (date >= self.start)
        if self.end is not None:
            isInside = isInside and (date <= self.end)
        return isInside

class DateRangeCollection():

    def __init__(self, starts=[], ends=[]):

        self.dateRanges = list()
        for start, end in zip(starts, ends):
           self.dateRanges.append(DateRange(start=start, end=end))

    def __iter__(self):
        for dateRange in self.dateRanges:
            assert isinstance(dateRange, DateRange)
            yield dateRange

    def inside(self, date):
        for dateRange in self.dateRanges:
            if dateRange.inside(date=date):
                return True
        return False

if __name__ == '__main__':

    date = Date(2000,7,1)
