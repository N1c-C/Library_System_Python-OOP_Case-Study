"""
Classes that provide methods to create and maintain loans between Member() and BookItem() instances
"""

from Aggregator import _Aggregator
from CsvIO import _CsvIO
from JsonIO import _JsonIO
from Singleton import _Singleton
from DateStamp import Date


class LoanItem:
    """ Holds the attributes of a single loan. Instantiated when a loan starts."""

    def __init__(self, book_uid, member_uid, start_date='default', return_date=0):
        """
        :param book_uid: int as str:
        :param member_uid: int as str:
        :param start_date: Int or 'default'
        :param return_date: Int

        :raises TypeError if the uid or date values are incorrect types
        """

        if not isinstance(book_uid, str) or not isinstance(member_uid, str):
            raise TypeError("LoanItem: Object_id should be in string format")

        self.book_uid = book_uid
        self.member_uid = member_uid

        if (start_date == 'default' or isinstance(start_date, int)) and isinstance(return_date, int):
            self.start_date = Date(start_date)
            self.return_date = Date(return_date)
        else:
            raise TypeError("LoanItem: Date arguments should be integers")

    def __str__(self):
        return str(self.__dict__)

    def as_dict(self):
        """ :returns object's attributes as a dictionary
                converts date objects to the date value stored in the object."""
        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        return dct

    def as_json_dict(self):
        """ :returns object's attributes as a dictionary
                Adds a 'class' key and value for the custom JSON decoder
                Converts date objects to the date value stored in the object."""
        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        dct['class'] = '__LoanItem__'
        return dct

    @staticmethod
    def create(attributes):
        """
        :returns a Loan instance created from an attributes dictionary
                keys = {'book_uid':, member_uid':, 'start_date':, 'return_date':}
                book_uid, member_uid values: int as a string
                return_date, start_date: int as string

        :raises Exception: If arg is not a dict
        """

        if isinstance(attributes, dict):  # Guardian check for correct type
            book_uid = attributes.get('book_uid', '')
            member_uid = attributes.get('member_uid', '')
            start_date = (int(attributes.get('start_date', '')))
            return_date = (int(attributes.get('return_date', '')))
            return LoanItem(book_uid, member_uid, start_date, return_date)
        else:
            raise Exception('Argument should be dictionary of attributes')

    def start_date_obj(self):
        """ :returns start_date object """
        return self.start_date

    def ret_date_obj(self):
        """ :returns return_date object """
        return self.return_date


class Loans(_Aggregator, _JsonIO, _CsvIO,  _Singleton):
    """
    Class to store and manipulate all book loans
        Inherits Singleton properties.
        Aggregates LoanItem  Objects.
        Loans are stored in self.collection{}.
            The Keys = 'book_uid-member_uid'
            Key values = list of LoanItem objects. The Current loan is the last item in the list
        _filename holds name of file for save / restore methods as a string
        """

    _filename = 'loans'  # Sets default file name
    collection = {}
    MAX_LOANS = 5  # The maximum number of loans a member can have.
    MAX_DURATION = 14  # The maximum number of days for a loan.

    def __str__(self):
        """ Unpacks self.collection for string calls """
        dct = {}
        for key in self.collection:
            dct[key] = [obj.as_dict() for obj in self.collection[key]]
        return str(dct)

    def read_csv(self, filename, **kwargs):
        """ Overloads Parent method to load csv data into collection.
                If the loan is not in self.collection then a Loan() instance is created using yhe Loan().create method
        """

        for line in super().read_csv(filename, **kwargs):
            self.add(LoanItem.create(line))

    def add(self, loan_item):
        """ Adds a Loan instance to collection{} with compound key
            The key value is a list of LoanItems.
            The current loan is appended to the end of the list
            loan_item must be an instance of LoanItem() """
        if isinstance(loan_item, LoanItem):
            key = loan_item.book_uid + '-' + loan_item.member_uid
            if key in self.collection:
                self.collection[key].append(loan_item)
            else:
                self.collection[key] = [loan_item]
        else:
            raise TypeError(f'Loans(): {loan_item} Must be a LoanItem() object')
        return

    def _make_json_dict(self):
        """:returns: self.collection unpacked as a json compatible dictionary"""
        dct = {}
        for key in self.collection:
            dct[key] = [obj.as_json_dict() for obj in self.collection[key]]
        return dct

    def search(self, book_uid, member_uid):
        """:returns: The list of LoanItems with the compound key"""
        return super().get(book_uid + '-' + member_uid)

    def start_loan(self, book_uid, member_uid):
        """ Starts a new loan using the default date values.
                start_date = current date,  return_date = 0 """
        self.add(LoanItem(book_uid, member_uid))

    def return_book(self, book_uid, member_uid):
        """
        :returns int: The length of loan in days
            Searches for most recent loan with book-member compound key.
            Sets the return_date to the current date"""

        loan_item = self.search(book_uid, member_uid)[-1]
        if int(loan_item.return_date.date) == 0:
            loan_item.return_date = Date()
        else:
            raise Exception('Loans(): Err with return date for item with key:'
                            f' {book_uid}-{member_uid}')
        return loan_item.return_date.as_val() - loan_item.start_date.as_val()

    def member_loans(self, member_uid):
        """
         Finds the active loans for a library member

        :param member_uid: int as str: Member id -
        :return: A list of the current loan instances associated with the member arg .
        """

        current_loans = []

        for key in self.collection:
            # Slices out the right side of the hyphen to get member_uid part only of the compound key
            # Looks for books with the return_date set to 0 i.e. still on loan
            if key[key.search('-') + 1:] == member_uid:
                if int(self.collection[key][-1].return_date.date) == 0:
                    current_loans.append(self.collection[key][-1])
        return current_loans

    def on_loan_to(self, book_uid):
        """
        Finds which member currently has a particular book on loan

        :param book_uid: int as string
        :return: int as str or None: The uid of the member who currently loans the book
                or None if the book is not loaned
        """

        for key in self.collection:
            # Slices out the left side of the hyphen to get book_uid part only of the compound key
            if key[:key.search('-')] == book_uid:
                # Returns uid if book still on loan
                if int(self.collection[key][-1].return_date.date) == 0:
                    return self.collection[key][-1].member_uid

        return None
