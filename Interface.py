from JsonIO import _JsonIO
from Library import BookItem
from Membership import Membership, Member
from Notifications import CardNotification, FineNotification
from Observer import Subject


class MembersInterface(_JsonIO):

    def __init__(self, membership, notify):
        """Provides a conceptual interface for library membership functions.
            :param membership: Membership() instance containing all members
            :param notify: Subject() instance that deals with notifications on Event triggers

            :raises TypeError: if membership or notify are not the correct type of object"""

        if isinstance(membership, Membership):
            self.membership = membership
        else:
            raise TypeError("MembersInterface(): Invalid membership type passed:")

        if isinstance(notify, Subject):
            self.notify = notify
        else:
            raise TypeError("MembersInterface(): Invalid subject type passed:")

        # List to hold daily applications. Cleared once send_list has been called
        self.new_members = []
        self.filename = 'new_members'

    def save(self):
        """Saves new_members to a JSON file"""
        super().save_to_file(self.filename)

    def restore(self, file=''):
        """Restores new_members from a JSON file
        :raises FileNotFound; If the backup file does not exist"""
        backup = self.new_members.copy()
        try:
            self.new_members = super().restore(self.filename)
        except FileNotFoundError:
            self.new_members = backup
            print(f'Unable to restore from file {self.filename}')

    def _make_json_dict(self):
        """ :returns: The new member list unpacked into a list of dictionaries for json compatibility """

        return [member.as_json_dict() for member in self.new_members]

    def add_member(self, **kwargs):
        """
        Creates a new library Member() instance and adds it to the membership.

            :param kwargs: Should match Member attribute keywords
            first_name = ' ',last_name = ' ', gender = ' ', email = ' '
        """
        new_mem = Member().create(kwargs)
        new_mem.uid = self.membership.next_id()
        self.membership.add(new_mem)
        self.membership.save()
        self.new_members.append(new_mem)
        self.save()
        self.restore()

    def new_member_list(self):
        """
        Obtains the current list of new applications for card manufacture/further processing.
                Currently only prints the data.
                Clears self.new_members afterwards
        """

        print('\nDetails for New Membership Cards\n')
        for member in self.new_members:
            print(f'{member.first_name} {member.last_name} with card number:'
                  f'{member.uid}1')

        self.new_members = []
        # Re-save to clear list

    def update_card(self, *args):
        """
        Updates the card_number for members. Automatically increments issue number and adds it to the end
        of member_uid to form card_id

        :param args: list of member_ids in string format who have new cards.
        """
        for member_uid in args:
            member = self.membership.search(member_uid)
            # gets the last digit in card_number and adds 1
            member.card_number = member.uid + str(int(member.card_number[-1]) + 1)

            # Notifications
            self.notify.send_email('NewCards', CardNotification(member))
            print('\n', '-' * 70)
            print('Console')
            print(f'\nCard details for {member.first_name} {member.last_name} '
                  f'have been updated with card number: {member.card_number}')

        self.membership.save()

    def waiting_for_card(self):
        """:returns: List of str: A list of the member ids who are waiting for a card to be issued."""

        card_lst = []
        for uid in self.membership.all_members():
            if self.membership.all_members()[uid].card_number == '0':
                card_lst.append(str(uid))
        return card_lst


class LoansInterface:
    def __init__(self, loans, membership, library, reservations, notify):
        """
        Provides an interface for borrowing and returning books
        :param loans: Instance of the Library Loans Object
        :param membership: Instance of the Membership
        :param library: Instance of a Library
        :param reservations: Instance of the reservations
        :param notify: Instance of a Subject for event notifications
        """

        self.loans = loans
        self.membership = membership
        self.library = library
        self.notify = notify
        self.lib_reservations = reservations
        self.DAILY_FINE = 1.0  # Fine amount / day for late returns

    def _has_max_loans(self, member):
        """
        Test to see if a member has the maximum number of loans
        :param member: A Member() instance
        :return: Bool:
        """

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
        """
        Retrieves the last recorded loan between member and book and calculates the fine for an overdue book.
        Prints to the console and sends a Notification to the member
            Searches on the compound key: 'book_uid-member_uid'
            Adds any fine to member's fine total.
            Saves the membership data
        :param book: A Book Instance
        :param member: A member Instance
        """

        last_loan = self.loans.search(book.uid, member.uid)[-1]

        days_over_due = (last_loan.return_date.as_val()) - (last_loan.start_date.as_val()) - self.loans.MAX_DURATION
        fine = days_over_due * self.DAILY_FINE
        print('\n', '-' * 70)
        print(f'\nFine due for book: {book.title}\n'
              f'For: {member.first_name} {member.last_name}\n'
              f'Borrowed on: {last_loan.start_date.as_date()}  '
              f'Returned on: {last_loan.return_date.as_date()}  '
              f'Days overdue: {days_over_due}  Fine: £{fine}')
        member.add_fine(fine)

        # Send Notification
        self.notify.send_email('Loans', FineNotification(member, book, days_over_due, fine))

    def checkout_books(self, member_of_public, *presented_books):
        """
        Scans the member_of_public & presented books.
            Retrieves the relevant member / books instances to simulate library kiosk.
            Checks for fines due, number of loans and book's status.
            Starts a loan if all conditions are ok. Saves the data to file

        :param member_of_public: a Member() instance.
        :param presented_books: a BookItem() instance or list of BookItem() instances
        :raises TypeError: If incorrect instance type are passed
        """

        if isinstance(member_of_public, Member):
            # retrieves member instance after scanning their card
            member = self.membership.search(member_of_public.scan())
        else:
            raise TypeError("Invalid Class: Expecting object of type Member() checkouts")

        if member.has_fine():
            print(f'{member.first_name} {member.last_name} has an '
                  f'overdue fine of £{member.fines}.\n Payment must be made before books can be loaned')
        else:
            for uid in presented_books:

                # retrieves book instance after scanning barcode
                book = self.library.search(uid.scan())
                # check member does not exceed loans.MAX_LOANs

                if not self._has_max_loans(member):

                    if book.is_on_loan():
                        libmem = self.membership.search(self.loans.on_loan_to(book.uid))
                        print(f'{book.title}: is already on loan', end='')
                        print(f' to {libmem.first_name} {libmem.last_name}: Unable to loan it')

                    if book.is_available():
                        # starts loan & updates: member.loans, book.status
                        self.loans.start_loan(book.uid, member.uid)
                        member.inc_loans()
                        book.set_on_loan()

                        # Add member to Loans Observers for overdue books etc
                        self.notify.register('Loans', member.uid)

                    if book.is_reserved():
                        """" check to see if the member is the first person
                            in the reservation que. If they are then they
                            can loan the book"""

                        # Retrieve the next reservation for the book
                        lib_res = self.lib_reservations.next_res(book.uid)
                        if lib_res.member_uid == member.uid:
                            # starts loan & updates: member.loans, book.status
                            self.loans.start_loan(book.uid, member.uid)
                            member.inc_loans()
                            book.set_on_loan()
                            # Remove person from front of reservation queue
                            self.lib_reservations.cancel_res(book.uid, member.uid)
                            # Add the member to the Loans Observers
                            self.notify.register('Loans', member.uid)
                        else:
                            print('\n', '-' * 70)
                            print('Console:')
                            print('The book is reserved by another member.')
                            if member.uid in self.lib_reservations.search(book.uid):
                                print('\n Your reservation is recorded.'
                                      'You will be notified when the book is available for you to loan')
                            else:
                                print('Would the member like to reserve this book?')

                else:
                    break  # Max loans reached. Stop checking out books
        self.loans.save()
        self.membership.save()
        self.library.save()

    def return_books(self, *presented_books):
        """
        Scans the presented books and obtains the uid
            Sets loan return_date to current date.
            If a book is overdue then adds a fine to the library member at the daily rate
            saves the data to file
        :param presented_books: str: A list of book ids to be returned
        :return:
        """

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


class ReservationInterface:
    def __init__(self, reservations, membership, library):
        """
        Provides an interface for reserving books

        :param reservations: Reservations() instance containing book reservations
        :param membership: Membership() instance containing all members'
        :param library: Library() instance containing all books
        """

        self.reservations = reservations
        self.membership = membership
        self.library = library

    def make_reservation(self, member_of_public, book_uid):
        """
         Scans the member_of_public and makes a reservation for a given book.
                If the book is already reserved then the member is added to the book's queue.
                Saves the updated reservations to file

        :param member_of_public: Member() instance
        :param book_uid: int as str:
        """
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
        if not book.is_on_loan():
            book.set_reserved()
        # Stores reservation to JSON file
        self.reservations.save()
