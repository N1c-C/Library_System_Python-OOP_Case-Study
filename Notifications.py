"""

"""


class FineNotification:
    def __init__(self, member, book, days_over_due, fine):
        """Encapsulates an overdue book message to a member"""
        self.all = False  # Flag to broadcast to all
        self.fine = fine
        self.days = days_over_due
        self.book = book
        self.member = member
        self.message = (f'\nEmailed to: {self.member.email} '
                        f'\nDear {self.member.first_name} {self.member.last_name},\n'
                        f'You returned the book {self.book.title} {self.days} days late.\n'
                        f'There is now a fine due of: £{self.fine}\n')


class ResNotification:
    def __init__(self, member, book, res):
        """Encapsulates a reservations message to a member"""
        self.all = False  # Flag to broadcast to all
        self.res = res
        self.book = book
        self.member = member
        self.message = (f'\nEmailed to: {self.member.email} '
                        f'\nDear {self.member.first_name} {self.member.last_name},\n'
                        f'{self.book.title} which you reserved on {self.res.date_made.as_date()}\n'
                        f'is now available for you pick up.\n')


# class BookNotification:
#     def __init__(self, book):
#         """Encapsulates a reservations message to a member"""
#         self.all = True  # Flag to broadcast to all
#         self.book = book
#         self.member = member
#         self.message = (f'{self.book.title} which you requested,'
#                         f' is now available for you to loan.\n')


class CardNotification:
    def __init__(self, member):
        """Encapsulates a message to a member"""
        self.all = False
        self.member = member
        self.message = (f'\nEmailed to: {self.member.email}'
                        f'\nDear {self.member.first_name},\n'
                        'Your new library card is available to be picked up \n'
                        f'Card number: {self.member.card_number}\n')
