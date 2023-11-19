

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

lib_loans.read_csv('bookloans.csv',Start_line = '0', Fields=[
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

notify = Subject('Subject Observers')

# Setup Observer Events
notify.add_events('Loans', 'Reservations', 'Books')

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
        books.append(lib_main.search(str(random.randint(1, 100)))) # random book_uid

    LoansMenu.checkout_books(person, *books)



