from Aggregator import Aggregator
from Observer import Observer


class Member(Observer):
    """ Holds the attributes of one library member as strings.
        uid (unique number), first_name, last_name, gender, email,
        card_number, no_of_loans.
        card_number = member_uid + issue number
        no_of_loans: current number of loans a member has
        fines: the amount owed from fines in pounds"""

    def __init__(self, uid='', first_name='', last_name='', gender='',
                 email='', card_number='', no_of_loans='0', fines='0.0'):
        self.uid = uid  # int as a string
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.email = email
        self.card_number = card_number  # int as a string
        self.no_of_loans = no_of_loans  # int as string
        self.fines = fines  # float as string

    def __str__(self):
        """returns a dictionary of attributes as a string"""
        return str(self.__dict__)

    def scan(self):
        """ Returns member_uid """
        return self.uid

    def as_dict(self):
        """Returns the Members' attributes as a dictionary."""
        return self.__dict__

    def as_json_dict(self):
        """Returns the Members' attributes as a dictionary. Adds a class value
        for custom JsonDecoder"""
        dct = self.__dict__.copy()
        dct['class'] = '__Member__'
        return dct

    def loans(self):
        """Returns the number of loans a member has as an integer"""
        return int(self.no_of_loans)

    def inc_loans(self):
        """ Increments self.no_of_loans by 1"""
        self.no_of_loans = str(int(self.no_of_loans) + 1)

    def dec_loans(self):
        """ Decrements self.no_of_loans by 1"""
        self.no_of_loans = str(int(self.no_of_loans) - 1)

    def add_fine(self, amount):
        """Adds amount to self.fines.  amount: float or integer"""
        self.fines = str(float(self.fines) + amount)

    def sub_fine(self, amount):
        """Subtracts amount from self.fines.  amount: float or integer"""
        self.fines = str(float(self.fines) - amount)

    def has_fine(self):
        """Returns bool: True if member has fines"""
        return True if float(self.fines) > 0 else False

    @staticmethod
    def create(attributes):
        """ Returns a Member() instance created from a attributes dictionary
            keys = {'uid':,'first_name':, 'last_name':, 'gender':,
                    'email':, 'card_number':}
            If any key is missing, '' assigned as default value """

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


class Membership(Aggregator):
    """ Inherits Singleton properties. Single instance of class stored in
        Singleton class _instances {}.
        Aggregates Member Objects
        _filename holds name of file for save / restore methods as a string
        All members are stored in collection{} as a Member object with 'member.uid'
        as keys"""

    _filename = 'members'  # Sets default file name
    collection = {}  # Dictionary of Member objects in the library

    def add(self, member):
        """ Adds a member object to collection{} with primary_id as key
         If not a member instance raises an Exception"""
        if isinstance(member, Member):
            super().add(member.uid, member)
        else:
            raise Exception(f'{member} Must be a Member() object')
        return

    def read_csv(self, filename, **kwargs):
        """ Overloads Parent method to load csv data into collection.
            if member not in collection generates Member() object,using
            Member().create static method"""

        for line in super().read_csv(filename, **kwargs):
            self.add(Member.create(line))
        return

    def next_id(self):
        """ Returns the next unique Id for a new member as a string.
            Simple algorithm of incrementing by 1. Does not reuse old numbers"""

        last_id = max(int(key) for key in self.collection)
        return str(last_id + 1)

    def all_members(self):
        """Returns the self.collection dictionary"""
        return self.collection

