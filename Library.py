"""Definitions for the Library Classes of the Entities and their Relationships"""

from Aggregator import Aggregator
from JsonIO import JsonIO
from Membership import Membership, Member
from Notifications import CardNotification, FineNotification


class Library(Aggregator):
    """  Encapsulates a library and Aggregates 'BookItem' Objects
        The books are stored in self.collection dictionary with 'BookItem.uid' as the key and BookItem as the value"""

    _filename = 'books'  # Sets default file name for saving and restoring JSON data
    collection = {}  # Dictionary of BookItem objects in the library

    def add(self, book):
        """ Adds a BookItem to self.collection by checking the type is correct then calling the parent class add method
        :param book: BookItem: The book object to be added to the Library
        :raises Exception; If the object is not a BookItem instance"""

        if isinstance(book, BookItem):
            super().add(book.uid, book)
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


class MembersInterface(JsonIO):

    def __init__(self, membership, notify):
        """Provides an conceptual interface for library membership functions.
            membership: Membership() instance containing all members"""

        if isinstance(membership, Membership):
            self.membership = membership
        else:
            raise TypeError("MembersInterface(): Invalid type passed:")

        # List to hold daily applications. Cleared once send_list has been called
        self.new_members = []
        self.filename = 'new_members'
        self.notify = notify

    def save(self):
        """Saves self.new_members to self.filename in a JSON file"""
        super().save(self.filename)

    def restore(self):
        """Restores self.new_members from JSON file with name self.filename"""
        backup = self.new_members.copy()
        try:
            self.new_members = super().restore(self.filename)
        except FileNotFoundError:
            self.new_members = backup
            print(f'Unable to restore from file {self.filename}')

    def _make_json_dict(self):
        """ Returns collection unpacked into a list of dictionaries
            for json compatibility """
        return [member.as_json_dict() for member in self.new_members]

    def add_member(self, **kwargs):
        """ Creates a new library Member() instance. Adds it to the membership
            and self.new_members list.
            *kwargs: Should match Member attribute keywords
            first_name = ' ',last_name = ' ', gender = ' ', email = ' '"""
        new_mem = Member().create(kwargs)
        new_mem.uid = self.membership.next_id()
        self.membership.add(new_mem)
        self.membership.save()
        self.new_members.append(new_mem)
        self.save()
        self.restore()

    def send_list(self):
        """Prints out the days list of new applications for the card
        manufacturer Clears self.new_members afterwards"""
        print('\nDetails for New Membership Cards sent to printers\n')
        for member in self.new_members:
            print(f'{member.first_name} {member.last_name} with card number:'
                  f'{member.uid}1')

        self.new_members = []
        # Re-save to clear list

    def update_card(self, *args):
        """Updates the card_number for members. Automatically increments issue
            number and adds it to the end of member_uid to form card_id
            *args list of member_ids with new cards."""
        for member_uid in args:
            member = self.membership.search(member_uid)
            # gets the last digit in card_number and adds 1
            member.card_number = member.uid + str(int(member.card_number[-1]) + 1)

            # Notifications
            self.notify.sendEmail('NewCards', CardNotification(member))
            print('\n', '-' * 70)
            print('Console')
            print(f'\nCard details for {member.first_name} {member.last_name} '
                  f'have been updated with card number: {member.card_number}')

        self.membership.save()

    def waiting_for_card(self):
        """Returns list of member.uids as strings: All members waiting for
            a card to be issued. Checks card number = '0'"""

        card_lst = []
        for uid in self.membership.all_members():
            if self.membership.all_members()[uid].card_number == '0':
                card_lst.append(str(uid))
        return card_lst


class LoansInterface(object):
    def __init__(self, loans, membership, library, reservations, notify):
        """ loans: Loans() Instance - Aggregator of LoanItems()
            membership: Membership() - Aggregator of Members()
            library: Library() - Aggregator of BookItems()
            Provides an interface for borrowing and returning books"""

        self.loans = loans
        self.membership = membership
        self.library = library
        self.notify = notify
        self.lib_reservations = reservations
        self.DAILY_FINE = 1.0  # Fine amount / day for late returns

    def _has_max_loans(self, member):
        """ loans_obj: Loans() instance. member: Member() instance
            Tests if members loans < max allowed
            Returns bool: If True, prints out the list of books on loan """

        if member.loans() >= self.loans.MAX_LOANS:
            print('\n', '-' * 70)
            print(f'\n{member.first_name} {member.last_name} has '
                  'the maximum number of books on loan:\n')
            for loan_item in self.loans.member_loans(member.uid):
                book = self.library.search(loan_item.book_uid)
                print(f'{book.uid}, {book.title} by {book.author}')
            print('\n')
            return True
        return False

    def _fine_due(self, book, member):
        """ Retrieves the last loan between member and book
            Searches on the compound key: 'book_uid-member_uid
            Calculates the fine for an overdue book. Prints to console
            Adds fine to member.fines, saves the membership data"""

        last_loan = self.loans.search(book.uid, member.uid)[-1]

        days_over_due = (last_loan.return_date.as_val()) - (
            last_loan.start_date.as_val()) - 14
        fine = days_over_due * self.DAILY_FINE
        print('\n', '-' * 70)
        print(f'\nFine due for book: {book.title}\n'
              f'For: {member.first_name} {member.last_name}\n'
              f'Borrowed on: {last_loan.start_date.as_date()}  '
              f'Returned on: {last_loan.return_date.as_date()}  '
              f'Days overdue: {days_over_due}  Fine: £{fine}')
        member.add_fine(fine)

        # Send Notification
        self.notify.sendEmail('Loans', FineNotification(member, book, days_over_due, fine))
        return

    def checkout_books(self, member_of_public, *presented_books):
        """ member_of_public: a Member() instance. - represents a real person
            presented_books: BookItem() instances. - books they want to loan
            Scans the member_of_public & presented books for id.
            Retrieves the relevant member / books instances to simulate library kiosk.
            Checks for fines due, number of loans and book's status.
            Starts a loan if all conditions are ok. Saves the data to file"""

        if isinstance(member_of_public, Member):
            # retrieves member instance after scanning their card
            member = self.membership.search(member_of_public.scan())
        else:
            print("Invalid Class: Expecting object of type Member() checkouts")
            return

        if member.has_fine():
            print(f'{member.first_name} {member.last_name} has an '
                  f'overdue fine of £{member.fines}')
        else:
            for item in presented_books:
                if not isinstance(item, BookItem):
                    print('Invalid Class: Expecting presented book of type'
                          'BookItem() checkouts')
                    continue
                # retrieves book instance after scanning barcode
                book = self.library.search(item.scan())
                # check member does not exceed loans.MAX_LOANs

                if not self._has_max_loans(member):

                    if book.is_available():
                        # starts loan & updates: member.loans, book.status
                        self.loans.start_loan(book.uid, member.uid)
                        member.inc_loans()
                        book.set_onloan()

                        # Add member to Loans Observers for overdue books etc
                        self.notify.register('Loans', member.uid)
                    else:
                        """" check to see if the member is the first person
                            in the reservation que. If they are then they
                            can loan the book"""

                        # Retrieve the next reservation for the book
                        lib_res = self.lib_reservations.next_res(book.uid)
                        if lib_res.member_uid == member.uid:
                            # starts loan & updates: member.loans, book.status
                            self.loans.start_loan(book.uid, member.uid)
                            member.inc_loans()
                            book.set_onloan()
                            # Remove person from front of reservation queue
                            self.lib_reservations.cancel_res(book.uid, member.uid)

                            # Add to Loans Observers
                            self.notify.register('Loans', member.uid)

                        print(f'{book.title}: is {book.status}', end='')
                        if book.is_onloan():
                            print(f' to {member.first_name} {member.last_name}')
                        else:
                            print(f': {member.first_name} {member.last_name} unable to loan it')
                else:
                    break  # Max loans reached. Stop checking out books
        self.loans.save()
        self.membership.save()
        self.library.save()
        return

    def return_books(self, *presented_books):
        """ presented_books: BookItem instances - books being returned
            Scans the presented books for id. Uses it to obtain uid
            Sets loan return_date to current date.
            If overdue adds fine to library member at £1 per day
            saves the data to file"""

        for item in presented_books:
            if not isinstance(item, BookItem):
                print('Invalid Class: Expecting presented book of type'
                      'BookItem() returns')
                continue
            # Retrieves book and member instances

            book = self.library.search(item.scan())

            member = self.membership.search(self.loans.on_loan_to(book.uid))
            # Returns book and tests to see if it's overdue

            if self.loans.return_book(book.uid, member.uid) > self.loans.MAX_DURATION:
                self._fine_due(book, member)
            member.dec_loans()

            # Deregister Subscriber from loans event if they currently have no books
            if member.loans == 0:
                self.notify.deregister('Loans', member.uid)
            # Update books status is: Available or Reserved
            self.lib_reservations.status_update(book)

        self.loans.save()
        self.membership.save()
        self.library.save()
        return


class ReservationInterface:
    def __init__(self, reservations, membership, library):
        """ reservations: Reservations() instance containing all members
            membership: Membership() instance containing all members
            library: Library() instance containing all books
            Provides an interface for borrowing and returning books"""

        self.reservations = reservations
        self.membership = membership
        self.library = library

    def make_reservation(self, member_of_public, book_uid):
        """ Scans the member and makes a reservation for the book with uid.
            If the book is already reserved adds them to the book's queue.
            uid: int as string. member_of_public: Member() instance"""
        member = self.membership.search(member_of_public.scan())
        book = self.library.search(book_uid)
        self.reservations.make_reservation(book.uid, member.uid)
        res_item = self.reservations.get_reservation(book.uid, member.uid)
        queue_pos = self.reservations.queue_pos(book.uid, member.uid)
        print('\n', '-' * 70)
        print(f'\nThe book: {book.title} is currently: {book.status}.\n')
        print(f'Reservation made by: {member.first_name} '
              f'{member.last_name} on {res_item.date_made.as_date()}\n'
              f'Currently in queue position: {queue_pos + 1}\n')
        if not book.is_available() or queue_pos > 0:
            print('You will be contacted when it becomes available')
        else:
            print('The book is available now')
        if not book.is_onloan():
            book.set_reserved()
        # Stores reservation to JSON file
        self.reservations.save()
