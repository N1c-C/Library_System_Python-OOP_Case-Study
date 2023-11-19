"""
Observer and Subject Classes to implement a notification system
"""
from JsonIO import _JsonIO


class Observer:
    """ Observer class to the Subject. Inherited by Members() to provide a notification system
            Currently a message is displayed on the console to simulate a notification"""

    def __init__(self):
        self.email = None
        self.first_name = None
        self.uid = None

    def send_email(self, notice):
        # If the message instance has an all flag set then all subscribers receive the message
        if notice.all:
            print(f'Emailed to {self.email}\n' 
                  f'Dear {self.first_name}\n'
                  f'{notice.message}')
        # If the message is for a specific member
        elif notice.member.uid == self.uid:
            print(notice.message)


class Subject(_JsonIO):
    def __init__(self, membership):
        """
        The Subject class (observable) of an Observer Pattern.
            Maintains a dictionary of events that the Observers can subscribe to
            The event is used as the key with a list of member unique ids as the value

        :param membership: Membership() Instance
        """

        self.events = {}
        self.filename = 'events'
        self.lib_membership = membership

    def save(self):
        """Saves the events a JSON file"""
        super().save_to_file(self.filename)

    def restore(self, file=''):
        """
        Restores events from a JSON file

        :raises: FileNotFound: If events JSON file is unavailable
        """
        backup = self.events.copy()
        try:
            self.events = super().restore(self.filename)
        except FileNotFoundError:
            self.events = backup
            print(f'Unable to restore from file {self.filename}')

    def _make_json_dict(self):
        """ :returns dict: Simply the 'self.events' dictionary """
        return self.events

    def add_events(self, *events):
        """
         Adds an event(s) that observers can subscribe too.
            Does not overwrite the list if it already exists

        :param events: str: The name(s) of observable event(s).
                            Added as a key(s) to self.events.
                            Key value =  list of observers subscribed to that event.
        """
        for event in events:
            if event not in self.events:
                self.events[event] = []
                self.save()

    def del_events(self, *events):
        """
         Removes the event(s) from the events dictionary if they exist.
                Deletes all subscribers to that event.

        :param events: str: The event keys to be removed from 'self.events'
        """
        for event in events:
            self.events.pop(event, None)
            self.save()

    def register(self, event, *observers):
        """
         Registers an observer(s) to an existing event's subscriber list:

        :param event: str: The name of an existing observable event
        :param observers: str: A Member's unique id (or list of several) to be added to event's list
        :raises: KeyError: If no such event exists
        """
        if event in self.events:
            for ob in observers:
                if ob not in self.events[event]:
                    self.events[event].append(ob)
                    self.save()
        else:
            raise KeyError(f'{event} list does not exist')

    def deregister(self, event, observer):
        """
        Removes an observer from event's list

        :param event: str: The name of an existing event
        :param observer: str: A member's unique id
        :raises: KeyError: If no such event exists
        """

        if observer in self.get_observers(event):
            self.get_observers(event).remove(observer)
            self.save()

    def get_observers(self, event):
        """
        Returns the uid of all the members subscribed to a particular event
            Returns an empty list if it does not exist.


        :param event: str: The name of an event in the event dict
        :return: List: A list of the uid 's for all the event's subscribed members
                        Returns and empty list if the event arg does not exist
        """

        return self.events.get(event, [])

    def send_email(self, event, message):
        """
        Sends the message to all subscribers of the event

        :param event: str:
        :param message: Notification(). Class that holds the message and intended recipient(s)

        """
        for observer in self.get_observers(event):
            self.lib_membership.search(observer).send_email(message)
