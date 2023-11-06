import time
import calendar

class Date:
    """ Holds a single date integer in Microsoft Excel epoch format as a str.
        date: integer - represents the Number of days since 1/1/1900.
        If no argument, current date set. Methods provided to set/return
        date in string format 'd/m/y' or integer value.
        Requires time and calendar modules. """

    def __init__(self, date='default'):

        if date == 'default':
            self.date = str(self._system_to_excel())
        elif isinstance(date, int):
            self.date = str(date)
        else:
            raise TypeError('Date() Argument should be an integer')

    def __str__(self):
        return self.date

    def _diff_in_days(self):
        """ Returns int: difference between Excel & O.S. epoch dates in days.
            O.S. independent: allows for different systems epoch standards
            Calculated as: number of days + leap days,  between dates """

        SYSTEM_EPOCH = time.gmtime(0).tm_year  # year of day 0 for current O.S.
        leap_days = 0

        for x in range(min(1900, SYSTEM_EPOCH), 1 + max(1900, SYSTEM_EPOCH)):
            # boolean expression for a leap year
            if x % 4 == 0 and x % 100 != 0 or x % 400 == 0:
                leap_days += 1

        # if os epoch is before 1900, leaps days should be subtracted.
        if SYSTEM_EPOCH < 1900:
            leap_days *= -1

        # + 1 day : Excel counts 1/1/1900 as day 1
        return (SYSTEM_EPOCH - 1900) * 365 + leap_days + 1

    def _system_to_excel(self, date=time.time()):  # Default = current time
        """ Returns int: The date in Excel epoch format.
            Optional date arg(int): number of secs since the o.s. epoch.
            Defaults to current date if no arg passed.
            Adds 1 day if date is after 28/02/1900 as Excel incorrectly
            calculates 1900 as a leap year"""

        no_of_days = int(date / (60 * 60 * 24)) + self._diff_in_days()

        # 29/02/1900 = day 59
        return no_of_days if no_of_days < 60 else no_of_days + 1

    def as_val(self):
        """Returns the date value as an int"""
        return int(self.date)

    def set_val(self, date):
        """ date = int. Overwrites self.date with argument. No conversion
            is performed """
        if isinstance(date, int):
            self.date = str(date)
        else:
            raise TypeError(f'Argument should be an integer. {type(date)} provided.')

    def set_date(self, date):
        """ Takes a date string d/m/y ex.('20/12/2000'). Converts to excel and
            sets the date. """
        try:

            # date_val = time.mktime(time.strptime(date + ' 00:0', '%d/%m/%Y %H:%M'))
            # converts to seconds since os epoch UTC time
            date_val = calendar.timegm(time.strptime(date, '%d/%m/%Y'))

            self.date = str(self._system_to_excel(date_val))

        except ValueError:
            print('Date should be in the format d/m/year')
        return

    def as_date(self):
        """ Returns self.date as string in 'd/m/y' format
         Adjustment of one day if date is before 29/02/1900  """

        no_of_days = (int(self.date) - self._diff_in_days())
        if int(self.date) > 59:  # > 28/02/1900
            no_of_days -= 1
        tse_in_secs = no_of_days * (60 * 60 * 24)  # tse: time since epoch
        return time.strftime("%d/%m/%Y", (time.gmtime(tse_in_secs)))