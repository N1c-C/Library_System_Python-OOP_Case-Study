from Library import *

lib_main = Library.get_instance()
# print(A)

from Membership import Membership

lib_membership = Membership.get_instance()

# print(B)

lib_main.read_csv('books.csv', Start_line='1', Fields=[
    'uid', 'title', 'author', 'genre', 'subgenre', 'publisher'])

# Read membership csv file,
lib_membership.read_csv(
    'members.csv', Start_line='1', Fields=[
        'uid', 'first_name', 'last_name', 'gender', 'email', 'card_number'])

# create JSON files
lib_main.save()

lib_membership.save()

# Clear internal dictionaries
lib_membership.collection = {}
lib_main.collection = {}

# restore from JSON files
lib_membership.restore()
lib_main.restore()

from Loans import Loans

# create a Loans object
lib_loans = Loans()

# Import loans.csv test file. Setting the correct field names.
# 'Start_line = 0' as no column names are provided

lib_loans.read_csv('bookloans.csv', Start_line='0', Fields=[
    'book_uid', 'member_uid', 'start_date', 'return_date'])

# Save internal dictionary
lib_loans.save()

# Clear internal dictionary
lib_loans.collection = {}

# Restore dictionary
lib_loans.restore()

# Look at first five items in lib_loans internal dictionary
# We display the lastest loan between the Member and a Book

# i = 0
# for i, entry in enumerate(lib_loans.collection.items()):
#     print(entry[0],  # The Compound UID
#           entry[1][-1].start_date.as_date(),
#           entry[1][-1].return_date.as_date(),
#           lib_main.search(entry[1][-1].book_uid).title,
#           lib_membership.search(entry[1][-1].member_uid).last_name
#           )
#     if i == 4:
#         break

# Search for single Loanitem with the uids of the library member and book

# print()
# print(lib_loans.search('1','101'))


# Clear Loans.collection as the data is not useful for the tasks
# Json file renamed to Loans_test.json

lib_loans.collection = {}

from Interface import LoansInterface
import random
from Observer import Subject
from Reservations import Reservations

notify = Subject(lib_membership)

# Setup Observer Events
notify.add_events('Loans', 'Reservations', 'Books', 'NewCards')

lib_reservations = Reservations(lib_main, lib_membership, notify)

# Create a subject instance with the filename to save to.

# Test function: Simulates a selection of people with random numbers of books
# Random choice set to 8 to test max number of loans


LoansMenu = LoansInterface(lib_loans, lib_membership, lib_main, lib_reservations, notify)

# list of member_uid's
members_of_the_public = ['20', '40', '60', '80', '100', '120', '140', '159', '180', '200']

for member_uid in members_of_the_public:
    # Retrieves the Member instance with the member_uid
    person = lib_membership.search(member_uid)

    # Creates a list of books each member wants to loan
    books = []
    for y in range(random.randint(1, 8)):  # Random choice set to 8 to test max number of loans
        books.append(lib_main.search(str(random.randint(1, 100))))  # random book_uid

    LoansMenu.checkout_books(person, *books)

# Test that multiple loans of a book by the same person are recorded as
# seperate loans

LoansMenu.checkout_books(lib_membership.search('1'), lib_main.search('120'))
LoansMenu.return_books(lib_main.search('120'))
LoansMenu.checkout_books(lib_membership.search('1'), lib_main.search('120'))
LoansMenu.return_books(lib_main.search('120'))
LoansMenu.checkout_books(lib_membership.search('1'), lib_main.search('120'))
LoansMenu.return_books(lib_main.search('120'))

# Returns the instances of LoanItems with compound key '120-1'
print(lib_loans.search('120', '1'))

# Test for fines
# The same members of puplic now return their books.

for member_uid in members_of_the_public:
    # Get all the current loans for a member
    for loan in lib_loans.member_loans(member_uid):
        # Adjusts the loan start date by a random number of days (max 20) earlier.
        loan.start_date.set_val(loan.start_date.as_val() - random.randint(1, 20))
        LoansMenu.return_books(lib_main.search(loan.book_uid))

# Testing functionality
from Interface import MembersInterface

#  Instantiate Interface
MemMenu = MembersInterface(lib_membership, notify)

# Add members with test some test data

MemMenu.add_member(first_name='David', last_name='Jason', gender='Male', email='dj@omail.com')
MemMenu.add_member(first_name='Clare', last_name='Wilson', gender='Female', email='c.wilson@omail.com')
MemMenu.add_member(first_name='Kate', last_name='Wilson', gender='Female', email='k.wilson@omail.com')
MemMenu.add_member(first_name='Jude', last_name='Davis', gender='Female', email='jude@omail.com')
MemMenu.add_member(first_name='Fred', last_name='Flintstone', gender='Male', email='fred@dinomail.com')

# Check they have been added to the Membership database and the new members list

# They should have automatically been given the next member_uid.
# The last uid from the test data is 200, So numbers 201 to 205 should be issued.

for member in range(201, 206):
    print(lib_membership.search(str(member)))

print()
# Check the new members list

print(MemMenu.new_members)

# Testing members getting their new cards

MemMenu.update_card('201', '202', '203')

# Test members getting their next card issue

MemMenu.update_card('201', '202', '203')

# Testing reservations
from Reservations import Reservations
from Interface import ReservationInterface

# Instantiate Reservations
lib_reservations = Reservations(lib_main, lib_membership, notify)

# Instantiate the Interface
ResMenu = ReservationInterface(lib_reservations, lib_membership, lib_main)

# One Memeber loans a book, two others make reservations.
LoansMenu.checkout_books(lib_membership.search('203'), lib_main.search('110'))
ResMenu.make_reservation(lib_membership.search('201'), '110')
ResMenu.make_reservation(lib_membership.search('202'), '110')

# Two members reserve a book, this time it is available to start with.

ResMenu.make_reservation(lib_membership.search('201'), '111')
ResMenu.make_reservation(lib_membership.search('202'), '111')

# Both members try to loan the book. Clare in position 2 first, then David
LoansMenu.checkout_books(lib_membership.search('202'), lib_main.search('111'))
LoansMenu.checkout_books(lib_membership.search('201'), lib_main.search('111'))

# Check the reservations are stored
# There should be two for book '110' and one for book '111'

print(lib_reservations)

# A book is loaned out
LoansMenu.checkout_books(lib_membership.search('202'), lib_main.search('101'))

#  David makes a reservation
ResMenu.make_reservation(lib_membership.search('201'), '101')


# Fred makes a reservation for the same book
ResMenu.make_reservation(lib_membership.search('205'), '101')

# Book is returned
LoansMenu.return_books(lib_main.search('101'))

# David gets his email,loans the book and returns it

LoansMenu.checkout_books(lib_membership.search('201'), lib_main.search('101'))
LoansMenu.return_books(lib_main.search('101'))

# Fred sees the email and loans book

LoansMenu.checkout_books(lib_membership.search('205'), lib_main.search('101'))