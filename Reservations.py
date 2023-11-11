from Aggregator import Aggregator
from DateStamp import Date
from Notifications import ResNotification


class ReservationItem:

    def __init__(self, book_uid, member_uid, date_made='default'):
        """ Holds attributes of a book and the member that has reserved it.
            Instantiated when a reservation is made.
            uid, uid: int as strings
            date_made: Date() object set to current date on instantiation """

        if not isinstance(book_uid, str) or not isinstance(member_uid, str):
            raise TypeError("Reservation: Object_id should be in string format")

        self.book_uid = book_uid
        self.member_uid = member_uid
        self.date_made = Date(date_made)

    def as_dict(self):
        """ Returns instances' attributes as a dictionary
            Replaces date objects with the date value it stores"""
        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        return dct

    def as_json_dict(self):
        """ Returns instances' attributes as a dictionary. Adds class key for
            custom JSON decoder Replaces date objects with the date
            value it stores"""

        dct = self.__dict__.copy()
        for key in dct:
            if hasattr(dct[key], 'date'):
                dct[key] = dct[key].date
        dct['class'] = '__ReservationItem__'
        return dct

    @staticmethod
    def create(attributes):
        """ Returns a ReservationItem instance created from attributes dict
            keys = {'uid':, member_uid':, 'date_made': }
            book_uid, member_uid values: int as a string
            return / start date: int as string"""

        if isinstance(attributes, dict):  # Guardian check for correct type
            book_uid = attributes.get('book_uid', '')
            member_uid = attributes.get('member_uid', '')
            date_made = (int(attributes.get('date_made', '')))
            return ReservationItem(book_uid, member_uid, date_made)
        else:
            raise Exception('Argument should be dictionary of attributes')


class Reservations(Aggregator):
    """ Inherits Singleton properties. Single instance of class stored in
        Singleton._instances {}.
        Aggregates ReservationItem()  Instances.
        ReservationItems are stored in self.collection{}. Key = 'uid'
        Key value = list of ReservationItem objects for that book.
        Next member in queue: first item. Most recent reservation: last item.
        _filename holds name of file for save / restore methods as a string
        """

    _filename = 'reservations'  # default file name for JsonIO
    collection = {}

    def _init__(self, library, membership, notifications):
        """Binds library attribute to Library() instance"""
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
        """ Adds a Reservation object to collection{} with book_uid as key
            The current res_item is appended to the end of the list
            res_item must be an instance of ReservationItem() """
        if isinstance(res_item, ReservationItem):

            if res_item.book_uid in self.collection:
                self.collection[res_item.book_uid].append(res_item)
            else:
                self.collection[res_item.book_uid] = [res_item]
        else:
            raise TypeError(f'Reservations(): {res_item} Must be type ReservationItem()')
        return

    def _make_json_dict(self):
        """ Returns self.collection unpacked into a json compatible dict.
            Keeps primary key. Values = a list of ReservationItem objects
            as dictionaries"""
        dct = {}
        for key in self.collection:
            dct[key] = [obj.as_json_dict() for obj in self.collection[key]]
        return dct

    def make_reservation(self, book_uid, member_uid):
        """ uid, uid: int as string
            Makes a reservation for the book by the member.
            book_uid: int as string member_uid: int as string"""
        self.add(ReservationItem(book_uid, member_uid))
        # Called when NOTIFY Flag set
        self.notify.register('Reservations', member_uid)

    def cancel_res(self, book_uid, member_uid):
        """ book_uid, member_uid: int as string
            Cancels first reservation for the book by the member.
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
        """ Returns the ReservationItem instance at front of the queue, for
            the book with uid.
            None returned if there are no reservations
            book_uid: int as string"""

        return self.collection.get(book_uid, None)[0]  # Indexes the oldest reservation

    def queue(self, book_uid):
        """ Returns the queue of ReservationItem instances for the book
            with uid.
            None returned if there are no reservations
            book_uid: int as string"""
        return self.collection.get(book_uid, None)

    def queue_pos(self, book_uid, member_uid):
        """ Returns the queue position of a member for a given book_uid,
            Returns None if no reservation found
            book_uid: int as string member_uid: int as string"""
        try:
            for index, res_item in enumerate(self.queue(book_uid)):
                if res_item.member_uid == member_uid:
                    return index
            else:
                return None
        except Exception:
            raise TypeError("None type is not iterable ")

    def get_reservation(self, book_uid, member_uid):
        """ Returns the ReservationItem Instance for a book by a Member
            book_uid: int as string  member_uid: int as string"""
        return self.queue(book_uid)[self.queue_pos(book_uid, member_uid)]

    def has_reservations(self, book_uid):
        """Returns bool: True if book has a reservations list
            book_uid: int as string"""
        return True if book_uid in self.collection else False

    def status_update(self, book):
        """ Receives status update from loans when a book is checked in
            if book is reserved then sets  books status to reserved
            book: BookItem instance"""
        if self.has_reservations(book.uid):
            book.set_reserved()
            res = self.next_res(book.uid)
            member = self.lib_membership.search(res.member_uid)
            self.notify.sendEmail('Reservations', ResNotification(member, book, res))
        else:
            book.set_available()
