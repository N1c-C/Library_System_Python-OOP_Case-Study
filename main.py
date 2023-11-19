

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
