

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

i = 0
for i, entry in enumerate(lib_loans.collection.items()):
    print(entry[0],  # The Compound UID
          entry[1][-1].start_date.as_date(),
          entry[1][-1].return_date.as_date(),
          lib_main.search(entry[1][-1].book_uid).title,
          lib_membership.search(entry[1][-1].member_uid).last_name
          )
    if i == 4:
        break

# Search for single Loanitem with the uids of the library member and book

print()
print(lib_loans.search('1','101'))


# Clear Loans.collection as the data is not useful for the tasks
# Json file renamed to Loans_test.json

lib_loans.collection = {}