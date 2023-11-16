import time
import calendar


class Date:
    """ Class to hold a single date. Includes methods to convert between the Microsoft Excel format
    and the typical str format d/m/y """

    def __init__(self, date='default'):
        """ :param date: int: Excel format - represents the Number of days since 1/1/1900.
                If no date argument is provided then the current date is set
            :raises TypeError: If the supplied value is not an integer
        """
        if date == 'default':
            self.date = str(self._system_to_excel())
        elif isinstance(date, int):
            self.date = str(date)
        else:
            raise TypeError('Date() Argument should be an integer')

    def __str__(self):
        return self.date

    @staticmethod
    def _diff_in_days():
        """ Operating systems having different epoch standards.
            Unix: 1/1/1970
            Windows: 1/1/1601
            This method finds the difference between the OS epoch and the Excel Epoch (OS independent)
        returns int: difference between Excel & O.S. epoch dates in days.
            Calculated as: number of days + leap days,  between the two dates """

        SYSTEM_EPOCH = time.gmtime(0).tm_year  # year of day 0 for current O.S.

        # find the number of leap days between the two epochs
        leap_days = 0

        for x in range(min(1900, SYSTEM_EPOCH), 1 + max(1900, SYSTEM_EPOCH)):
            # boolean expression for a leap year
            if x % 4 == 0 and x % 100 != 0 or x % 400 == 0:
                leap_days += 1

        # if os epoch is before 1900, leaps days should be subtracted.
        if SYSTEM_EPOCH < 1900:
            leap_days *= -1

        # + 1 day : Excel counts 1/1/1900 as day 1 and not day 0
        return (SYSTEM_EPOCH - 1900) * 365 + leap_days + 1

    def _system_to_excel(self, date=time.time()):
        """ Calculates a date in Excel format
        :param date: int:  number of secs since the o.s. epoch.
            If no arg passed then the current date is found
        :returns int: The number of seconds since 1/1/1900.
            Adds 1 day if the date is after 28/02/1900 as Excel incorrectly
            calculates 1900 as a leap year"""

        no_of_days = int(date / (60 * 60 * 24)) + self._diff_in_days()

        # 29/02/1900 = day 59 - adjustment if the date is before the first recorded leap day
        return no_of_days if no_of_days < 60 else no_of_days + 1

    def as_val(self):
        """:returns int: The instances stored date"""
        return int(self.date)

    def set_val(self, date):
        """Assigns a value to the objects date attribute
        :param date: int: Value to overwrite self.date with.  No conversion is performed
        :raises TypeError: If an integer is not passed"""
        if isinstance(date, int):
            self.date = str(date)
        else:
            raise TypeError(f'Argument should be an integer. {type(date)} provided.')

    def set_date(self, date):
        """ Takes a date string  and converts it to Excel integer format and sets self.date.
            :param date: str: in the form of dd/mm/yyyy ex.('20/12/2000')
            :raises ValueException: If the arg is not in the correct format"""

        try:
            date_val = calendar.timegm(time.strptime(date, '%d/%m/%Y'))
            self.date = str(self._system_to_excel(date_val))

        except ValueError:
            print('Date should be in the format dd/mm/yyyy')
        return

    def as_date(self):
        """ :returns self.date as a string in 'dd/mm/yyyy' format
         An adjustment of one less day is made if the date is before 29/02/1900  """

        no_of_days = (int(self.date) - self._diff_in_days())
        if int(self.date) > 59:  # > 28/02/1900
            no_of_days -= 1
        tse_in_secs = no_of_days * (60 * 60 * 24)  # tse: time since epoch
        return time.strftime("%d/%m/%Y", (time.gmtime(tse_in_secs)))
