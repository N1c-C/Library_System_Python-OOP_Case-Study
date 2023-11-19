"""
Classes that provide methods to create and maintain the library membership
"""

from Aggregator import _Aggregator
from Observer import Observer
from CsvIO import _CsvIO
from JsonIO import _JsonIO
from Singleton import _Singleton


class Member(Observer):
    """ Holds the attributes of one library member as strings.
        Provides methods to access and adjust the attributes
        """

    def __init__(self, uid='', first_name='', last_name='', gender='',
                 email='', card_number='', no_of_loans='0', fines='0.0'):
        """

        :param uid: int as str:
        :param first_name: str:
        :param last_name: str:
        :param gender: str:
        :param email: str:
        :param card_number: int as str
        :param no_of_loans: int as str : Current number of books on loan
        :param fines: float : The amount owed from fines in pounds
        """
        self.uid = uid
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.email = email
        self.card_number = card_number
        self.no_of_loans = no_of_loans
        self.fines = fines

    def __str__(self):
        """:returns: dict: The dictionary of attributes as a string"""
        return str(self.__dict__)

    def scan(self):
        """ :returns: int as str: The members unique id """
        return self.uid

    def as_dict(self):
        """:returns dict: The Members' attributes as a dictionary."""
        return self.__dict__

    def as_json_dict(self):
        """:returns dict: The Members' attributes as a dictionary but with a 'class' key and value
        for the custom JsonDecoder"""
        dct = self.__dict__.copy()
        dct['class'] = '__Member__'
        return dct

    def loans(self):
        """:returns int: The number of current loans the member has"""
        return int(self.no_of_loans)

    def inc_loans(self):
        """ Increments the number of current loans by 1"""
        self.no_of_loans = str(int(self.no_of_loans) + 1)

    def dec_loans(self):
        """ Decrements the number of current loans by 1"""
        self.no_of_loans = str(int(self.no_of_loans) - 1)

    def add_fine(self, amount):
        """Adds a new fine to the total owed.
        :param amount: float or integer: The fine to be added"""
        self.fines = str(float(self.fines) + amount)

    def sub_fine(self, amount):
        """Subtracts paid fines from the total owed.
          :param amount: float or integer"""
        self.fines = str(float(self.fines) - amount)

    def has_fine(self):
        """:returns bool: True if member has fines"""
        return True if float(self.fines) > 0 else False

    @staticmethod
    def create(attributes):
        """ :returns : a Member() instance created from an attributes dictionary
                keys = {'uid':,'first_name':, 'last_name':, 'gender':,
                    'email':, 'card_number':}
                If any key is missing, '' assigned as default value
             :raises TypeError: If attributes is not a dict"""

        if isinstance(attributes, dict):
            uid = attributes.get('uid', '')
            first_name = attributes.get('first_name', '')
            last_name = attributes.get('last_name', '')
            gender = attributes.get('gender', '')
            email = attributes.get('email', '')
            card_number = attributes.get('card_number', '0')

            return Member(uid, first_name, last_name, gender, email,
                          card_number)
        else:
            raise TypeError('Argument should be dictionary of attributes')


class Membership(_Aggregator, _CsvIO, _JsonIO, _Singleton):
    """
    Stores Member() instances in the self.collection dictionary with Member().uid acting as the key
    with the instance as the value.

    Inherits Singleton properties.
    """

    _filename = 'members'  # Sets default file name for save/restore function
    collection = {}  # Dictionary of Member objects in the library

    def add(self, member):
        """
        Adds a member object to Membership()

        :raises TypeError: If arg is not a Member() instance
        """
        if isinstance(member, Member):
            super().add(member)
        else:
            raise TypeError(f'{member} Must be a Member() object')

    def read_csv(self, filename, **kwargs):
        """
        Loads Members instances from a csv file
            Calls the CsvIO.read_csv method to access the data and the Member Class method to instantiate
            a Member object.
            Adds the newly instantiated object to the membership
        :param filename: str: Name of the CSV file
        :param kwargs: See CsvIO.read_csv() :Options to choose the line in file to start from and define col headings
        """

        for line in super().read_csv(filename, **kwargs):
            self.add(Member.create(line))

    def next_id(self):
        """ :returns: int as str: The next unique id for a new member.
            Simple algorithm of incrementing by 1. Note - old numbers are not reused"""

        last_id = max(int(key) for key in self.collection)
        return str(last_id + 1)

    def all_members(self):
        """:returns: dict: The entire membership"""
        return self.collection
