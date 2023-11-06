from JsonIO import JsonIO


class Observer:
    """ Observer class to the Subject. Inherited by Members() to provide
        an email notification system"""
    def send_email(self, notice):
        if notice.all:  # if the message has an all flag it is printed
            print(f'Emailed to {self.email}\n' 
                  f'Dear {self.first_name}\n'
                  f'{notice.message}')
        elif notice.member.uid == self.uid:  # if the message is for the member it is printed
            print(notice.message)


class Subject(JsonIO):
    def __init__(self, filename, membership):
        """ The Subject (observable) of an Observer Pattern. To provide Member()
        Notifications. Multi-events can be observed. The observer lists
        are stored in a dictionary, self.events. The event is the key
        filename: name of file to save and restore subscribers to in json format"""

        self.events = {}
        self.filename = filename
        self.lib_membership = membership

    def save(self):
        """Saves self.events to self.filename in a JSON file"""
        super().save(self.filename)

    def restore(self):
        """Restores self.events from JSON file with name self.filename"""
        backup = self.events.copy()
        try:
            self.events = super().restore(self.filename)
        except FileNotFoundError:
            self.events = backup
            print(f'Unable to restore from file {self.filename}')

    def _make_json_dict(self):
        """ Returns collection unpacked into a list of dictionaries
            for json compatibility """
        return self.events

    def add_events(self, *events):
        """ Adds events that observers can subscribe too. Does not overwrite the
            list if it already exists
            events: string - name(s) of observable event(s). Added as a key(s)
            to self.events. Key value =  list of observers subscribed to that
            event."""
        for event in events:
            if event not in self.events:
                self.events[event] = []
                self.save()

    def del_events(self, *events):
        """ Removes the event(s) from the self.events dictionary if they exist.
            Deletes all subscribers to that event. Returns None if the event
            does not exist """
        for event in events:
            self.events.pop('key', None)
            self.save()

    def register(self, event, *observers):
        """ Register an observer(s) to an event subscriber list
            event: string - name of an observable event
            observer: string - A member's uid"""
        if event in self.events:
            for ob in observers:
                if ob not in self.events[event]:
                    self.events[event].append(ob)
                    self.save()
        else:
            raise KeyError(f'{event} list does not exist')

    def deregister(self, event, observer):
        """ Removes an observer from an event list
        event: string observer : string - member uid"""
        if observer in self.get_observers(event):
            self.get_observers(event).remove(observer)
            self.save()

    def get_observers(self, event):
        """ Returns the uid of all members subscribed to a particular event
            Returns an empty list if it does not exist.
            event: string - name of an event in the event dict."""
        return self.events.get(event, [])

    def send_email(self, event, message):
        """ Sends the message to all subscribers of the event
            event: string - a key in self events
            message can be anything as long as observer can deal with
            Returns with no error if event does not exist"""
        for observer in self.get_observers(event):
            self.lib_membership.search(observer).sendEmail(message)
