"""
Classes that provide methods to create and maintain reservations between Member() and ReservationItem() instances
"""


from Aggregator import _Aggregator
from DateStamp import Date
from Notifications import ResNotification


class ReservationItem:

    def __init__(self, book_uid, member_uid, date_made='default'):
        """
        Holds the attributes of a book and the member that has reserved it.
            Instantiated when a reservation is made.

            date_made: Date() object set to current date on instantiation
        :param book_uid: int as str: The unique id of a book
        :param member_uid: int as str: The unique id of the member making the reservation
        :param date_made: int or 'default': The date in seconds from 1/1/1900

        :raises: TypeError: If the UIDs are not in string format
        """

        if not isinstance(book_uid, str) or not isinstance(member_uid, str):
            raise TypeError("Reservation: Object_id should be in string format")

        self.book_uid = book_uid
        self.member_uid = member_uid
        self.date_made = Date(date_made)

    def as_dict(self):
        """
        :returns: The instances' attributes as a dictionary
                        Replaces Date objects with the date value it stores
        """

        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        return dct

    def as_json_dict(self):
        """
        :returns: The instances' attributes as a dictionary
                        Adds class key and value for the custom JSON decoder
                        Replaces Date objects with the date value it stores
        """

        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        dct['class'] = '__ReservationItem__'
        return dct

    @staticmethod
    def create(attributes):
        """
        Instantiates ReservationItem() instance from an attributes dict
                keys = {'uid':, member_uid':, 'date_made': }

        :param attributes: dict:
        :return: ReservationItem():

        :raises TypeError: If attributes is not a dict
        """

        if isinstance(attributes, dict):  # Guardian check for correct type
            book_uid = attributes.get('book_uid', '')
            member_uid = attributes.get('member_uid', '')
            date_made = (int(attributes.get('date_made', '')))
            return ReservationItem(book_uid, member_uid, date_made)
        else:
            raise TypeError('Argument should be dictionary of attributes')


class Reservations(_Aggregator):
    """
    Class to create and manipulate book reservations for library members
            ReservationItems are stored in self.collection dictionary.
                {Key = 'uid', Value = list of ReservationItem objects for that book}
                Next member in a books reservation queue: first list item.
    """

    _filename = 'reservations'  # default file name for JsonIO Save and restore functions
    collection = {}

    def _init__(self, library, membership, notifications):
        """
        :param library: Library() instance
        :param membership: Membership() instance
        :param notifications: Subject() instance
        :return:
        """

        self.library = library
        self.lib_membership = membership
        self.notifications = notifications

    def __str__(self):
        """ Unpacks self.collection for string calls """
        dct = {}
        for key in self.collection:
            dct[key] = [obj.as_dict() for obj in self.collection[key]]
        return str(dct)

    def add(self, res_item):
        """
        Adds a reservation for a book
            The reservation is appended to the end of the list for the given book

        :param res_item: ReservationItem()
        :raises TypeError; If res_item is not a ReservationItem() instance
        """
        if isinstance(res_item, ReservationItem):

            if res_item.book_uid in self.collection:
                self.collection[res_item.book_uid].append(res_item)
            else:
                self.collection[res_item.book_uid] = [res_item]
        else:
            raise TypeError(f'Reservations(): {res_item} Must be type ReservationItem()')
        return

    def _make_json_dict(self):
        """
        :return: self.collection unpacked into a JSON compatible dict.
                    Keeps primary key. Values = the list of ReservationItem(s) converted to dictionaries
        """
        dct = {}
        for key in self.collection:
            dct[key] = [obj.as_json_dict() for obj in self.collection[key]]
        return dct

    def make_reservation(self, book_uid, member_uid):
        """
        Makes a reservation between a book and a member and notifies the library member it has been made
        :param book_uid: int as str:
        :param member_uid: int as str:
        """

        self.add(ReservationItem(book_uid, member_uid))
        # Called when NOTIFY Flag set
        self.notify.register('Reservations', member_uid)

    def cancel_res(self, book_uid, member_uid):
        """
        Cancels the first reservation for the book by the member.

        :param book_uid: int as str
        :param member_uid: int as str
        """
        if book_uid in self.collection:

            for index, res_item in enumerate(self.collection[book_uid]):
                if res_item.member_uid == member_uid:
                    self.collection[book_uid].pop(index)
                    break
            # Removes the key if its list of values is empty:
            if len(self.collection[book_uid]) == 0:
                self.collection.pop(book_uid)

    def next_res(self, book_uid):
        """
        Gets the next reservation for a book

        :param book_uid: int as str:
        :return: The ReservationItem instance at front of the queue for the book
                      Returns None if there are no reservations
        """

        return self.collection.get(book_uid, None)[0]  # Indexes the oldest reservation

    def queue(self, book_uid):
        """
        Gets the queue of reservations for a book

        :param book_uid: int as str:
        :return: List: The list of reservations for the given book
                      Returns None if there are no reservations
        """
        return self.collection.get(book_uid, None)

    def queue_pos(self, book_uid, member_uid):
        """
         Gets the queue position of a member for a given book_uid,
                Returns None if no reservation found

        :param book_uid: int as str
        :param member_uid: int as str
        :return: int: the list index representing where the member is in the queue

        :raises ValueError: If the queue is empty
        """
        try:
            for index, res_item in enumerate(self.queue(book_uid)):
                if res_item.member_uid == member_uid:
                    return index
            else:
                return None
        except Exception:
            raise ValueError("The queue is empty")

    def get_reservation(self, book_uid, member_uid):
        """
        :param book_uid: int as str:
        :param member_uid: int as str:
        :return: The ReservationItem() instance for a book by a Member
        """
        return self.queue(book_uid)[self.queue_pos(book_uid, member_uid)]

    def has_reservations(self, book_uid):
        """
        :param book_uid: int as str
        :return: Bool: True if book has a reservations list
        """
        return True if book_uid in self.collection else False

    def status_update(self, book):
        """
         Performs a status update when a book is checked in
                If the book is reserved then sets the books status to reserved and
                notifies the next member in the queue
                Otherwise the book is made available

        :param book: BookItem() instance
        """
        if self.has_reservations(book.uid):
            book.set_reserved()
            res = self.next_res(book.uid)
            member = self.lib_membership.search(res.member_uid)
            self.notify.sendEmail('Reservations', ResNotification(member, book, res))
        else:
            book.set_available()
