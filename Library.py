"""Definitions for the Library and Book Classes along with the System interfaces used by
the Librarians to carry out their every day activities"""

from _Aggregator import _Aggregator
from _CsvIO import _CsvIO
from _JsonIO import _JsonIO
from _Singleton import _Singleton


class Library(_Aggregator, _CsvIO, _JsonIO, _Singleton):
    """  Encapsulates a library and Aggregates 'BookItem' Objects
        The books are stored in self.collection dictionary with 'BookItem.uid' as the key and BookItem as the value"""

    _filename = 'books'  # Sets default file name for saving and restoring JSON data
    collection = {}  # Dictionary of BookItem objects in the library

    def add(self, book):
        """ Adds a BookItem to self.collection by checking the type is correct then calling the parent class add method
        :param book: BookItem: The book object to be added to the Library
        :raises Exception; If the object is not a BookItem instance"""

        if isinstance(book, BookItem):
            super().add(book)
        else:
            raise Exception(f'{book} Must be a BookItem object')
        return

    def read_csv(self, filename, **kwargs):
        """ Iteratively loads book data into the Library from a csv file.
        :param filename: str: The name of the csv file
        :opt kwargs
        :Fields: List of str:  A list of column names for the csv values.
        :start_line: int:  The first line of csv to start reading the data from
            If book not in collection generates BookItem object,using
            BookItem().create static method"""
        for line in super().read_csv(filename, **kwargs):
            self.add(BookItem.create(line))
        return

    def next_id(self):
        """ The uid is a simple increasing integer. This method obtains the most recent uid and generates the next one
        by incrementing the uid by one. Note: Old numbers are not reused
        :returns : str: The next unique id for a new book.
            """

        last_id = max(int(key) for key in self.collection)
        return str(last_id + 1)


class BookItem:
    """
    Holds the attributes of one book as strings.
    """

    def __init__(self, uid='', title='', author='', genre='',
                 sub_genre='', publisher='', status='Available'):
        """
        :param uid: integer as a string
        :param title: str:
        :param author: str:
        :param genre: str:
        :param sub_genre: str:
        :param publisher:
        :param status: 1 of 3 states, 'Available' , 'On Loan', 'Reserved'
        """
        self.uid = uid  # int as a string
        self.title = title
        self.author = author
        self.genre = genre
        self.sub_genre = sub_genre
        self.publisher = publisher
        self.status = status

    def __str__(self):
        """:returns str: the objects attributes dictionary"""
        return str(self.__dict__)

    def scan(self):
        """ :returns str: the book's unique id """
        return self.uid

    def as_dict(self):
        """:returns dict: the books' attributes as a dictionary. """
        return self.__dict__

    def as_json_dict(self):
        """:returns dict: the books' attributes as a dictionary. Adds a class key and value
            for use by the custom JsonDecoder when reading saved files."""
        dct = self.__dict__.copy()
        dct['class'] = '__BookItem__'
        return dct

    def is_available(self):
        """:returns Bool: True if the book's status = Available"""

        return True if self.status == 'Available' else False

    def is_on_loan(self):
        """:returns Bool: True if the books status is On loan"""

        return True if self.status == 'On loan' else False

    def is_reserved(self):
        """:returns Bool: True if the books status is Reserved"""

        return True if self.status == 'Reserved' else False

    def set_available(self):
        """Sets the status flag to Available"""

        self.status = 'Available'

    def set_on_loan(self):
        """Sets the status flag to being on loan"""

        self.status = 'On loan'

    def set_reserved(self):
        """Sets the status flag to being reserved"""

        self.status = 'Reserved'

    @staticmethod
    def create(attributes):
        """ instantiates a BookItem() instance from attributes. It is called when adding instances
        to the Library() collection by the read.csv() and restore() methods.

        :param attributes: dict: A dictionary of attributes for a single book
                keys = {'uid':, 'title':, 'author':, 'genre':,'subgenre':,'publisher':}
        :returns a BookItem instance
                If any key is missing empty string assigned as default value
        :raises Exception: If attributes is not a dictionary"""

        if isinstance(attributes, dict):
            uid = attributes.get('uid', '')
            title = attributes.get('title', '')
            author = attributes.get('author', '')
            genre = attributes.get('genre', '')
            sub_genre = attributes.get('subgenre', '')
            publisher = attributes.get('publisher', '')
            return BookItem(uid, title, author, genre, sub_genre, publisher)
        else:
            raise Exception('Argument should be dictionary of attributes')


