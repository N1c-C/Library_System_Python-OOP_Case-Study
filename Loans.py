"""

"""

from Aggregator import Aggregator
from DateStamp import Date


class LoanItem:
    """    """

    def __init__(self, book_uid, member_uid, start_date='default', return_date=0):
        """ Holds attributes of a single loan. Instantiated when a loan starts.
            book_uid, uid: int as strings
            start_date, return_date: Date() objects
            return_date set to '0' until book returned """

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
        """ Returns object's attributes as a dictionary
            Replaces date objects with the date value stored in the object."""
        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        return dct

    def as_json_dict(self):
        """ Returns object's attributes as a dictionary. Adds a class value
            for custom Json decoder Replaces date objects with the date
            value stored in the object."""
        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        dct['class'] = '__LoanItem__'
        return dct

    @staticmethod
    def create(attributes):
        """ Returns a Loan instance created from attributes dictionary
            keys = {'book_uid':, member_uid':, 'start_date':, 'return_date':}
            book_uid, member_uid values: int as a string
            return / start date: int as string"""

        if isinstance(attributes, dict):  # Guardian check for correct type
            book_uid = attributes.get('book_uid', '')
            member_uid = attributes.get('member_uid', '')
            start_date = (int(attributes.get('start_date', '')))
            return_date = (int(attributes.get('return_date', '')))
            return LoanItem(book_uid, member_uid, start_date, return_date)
        else:
            raise Exception('Argument should be dictionary of attributes')

    def start_date_obj(self):
        """ Returns start_date object """
        return self.start_date

    def ret_date_obj(self):
        """ Returns return_date object """
        return self.return_date


class Loans(Aggregator):
    """ Inherits Singleton properties. Single instance of class stored in
        Singleton._instances {}.
        Aggregates LoanItem  Objects.
        Loans are stored in self.collection{}. Key = 'book_uid-member_uid'
        Key value = list of LoanItem objects. Current loan = last list item
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
            if loan not in collection generates Loan() object,using
            Loan().create static method"""

        for line in super().read_csv(filename, **kwargs):
            self.add(LoanItem.create(line))
        return

    def add(self, loan_item):
        """ Adds a Loan object to collection{} with compound key
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
        """Returns self.collection unpacked as a json compatible dictionary"""
        dct = {}
        for key in self.collection:
            dct[key] = [obj.as_json_dict() for obj in self.collection[key]]
        return dct

    def search(self, book_uid, member_uid):
        """Returns the list of LoanItems with compound key"""
        return super().search(book_uid + '-' + member_uid)

    def start_loan(self, book_uid, member_uid):
        """ Starts a new loan using default date values.
             start_date = current date,  return_date = 0 """
        self.add(LoanItem(book_uid, member_uid))

    def return_book(self, book_uid, member_uid):
        """ Returns integer: the length of loan in days
            Searches for most recent loan with book-member key.
            Sets the return_date to the current date"""

        loan_item = self.search(book_uid, member_uid)[-1]
        if int(loan_item.return_date.date) == 0:
            loan_item.return_date = Date()
        else:
            raise Exception('Loans(): Err with return date for item with key:'
                            f' {book_uid}-{member_uid}')
        return loan_item.return_date.as_val() - loan_item.start_date.as_val()

    def member_loans(self, member_uid):
        """ Returns a list of the current loans a member has.
            member_uid: int as string. Splits the compound key and searches on
            the member part for current loans (return_date = 0) """

        current_loans = []

        for key in self.collection:
            # Slices out the right side of the hyphen to get member_uid part only
            if key[key.find('-') + 1:] == member_uid:
                if int(self.collection[key][-1].return_date.date) == 0:
                    # adds the LoanItem to the list if return_date is set to 0
                    current_loans.append(self.collection[key][-1])
        return current_loans

    def on_loan_to(self, book_uid):
        """ book_uid: int as string
            Splits the compound_key
            Returns the uid of the member who currently loans the book
            with book_uid - as a string. None if not on loan"""

        for key in self.collection:
            # Slices out the left side of the hyphen to get book_uid part only
            if key[:key.find('-')] == book_uid:
                # Returns uid if book still on loan
                if int(self.collection[key][-1].return_date.date) == 0:
                    return self.collection[key][-1].member_uid

        return None
