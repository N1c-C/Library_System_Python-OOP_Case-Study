class Singleton:
    """An inherited Singleton class that allows one instance of a particular class to exist. The instances are
     stored in the class dictionary: _instances.
    Each instantiation of a new class creates a new entry in _instances."""

    _instances = {}

    def __new__(cls, *args, **kwargs):
        """Overloads __new__ to allow a new instance only if one does not already exist.
        __new__ is the first method called during class instantiation.
        :returns: A new instance of the class if it does not exist otherwise returns the instance that already exits"""

        if cls not in cls._instances:
            # uses super() to call the base class' __new__ method to instantiate a new instance
            instance = super().__new__(cls)
            cls._instances[cls] = instance
            return instance
        else:
            return cls._instances[cls]

    @classmethod
    def get_instance(cls):
        """ Class method to return the current instance. If the instance does not
            exist, a new one is created.
            :returns : the instance of cls"""

        if cls not in cls._instances:
            cls()
        return cls._instances[cls]

    @staticmethod
    def instance_exists(item_cls):
        """ Tests to see if a particular singleton class has already been instantiated
        :param item_cls : str: name of a class
        :returns :  Bool"""
        for c in Singleton._instances:
            if isinstance(Singleton._instances[c], eval(item_cls)):
                return True
        return False
