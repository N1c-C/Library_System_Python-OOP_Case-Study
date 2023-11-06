"""The Aggregator class contains a collection of other classes. This script defines a parent Aggregator
that is inherited by various entities and relationships"""

import CsvIO
import JsonIO
import Singleton


class Aggregator(CsvIO, JsonIO, Singleton):
    """ Inherits Singleton properties. Single instance of class referenced in Singleton._instances {}.

        Class Parameters:
        :param collection: dict: dictionary of objects where the keys are unique primary_ids associated with the
        respective values/object
        :param _filename: str:  Holds the name of the file for save / restore methods"""

    _filename = 'default'
    collection = {}  # dictionary of objects

    def __len__(self):
        """Returns the number of objects in self.collection """

        return len(self.collection)

    def __str__(self):
        """Converts the objects stored in self.collection to dictionaries enabling the data to be displayed.
        The objects stored must have an as_dict() method which returns the object's attributes dictionary

        :returns : str: A dictionary of dictionaries"""

        return str({key: self.collection[key].as_dict() for key in self.collection})

    def _make_json_dict(self):
        """ Converts the self.collection objects into dictionaries. The object's as_json_dict() method adds
        a 'class' key with an appropriate label for the value - in the form of '__Object Name__'.
        The label is used when reading the JSON file to create the correct object from the data stored.

         :returns dict: A dictionary of dictionaries"""

        return {key: self.collection[key].as_json_dict() for key in self.collection}

    def set_filename(self, filename):
        """ Method to set the default _filename name for save/restore methods"""

        self._filename = filename

    def restore(self):
        """ Restores self.collection{} from a JSON file, as a dict of objects.
            Calls JsonIO to read and return file data from self._filename
            JSON file should be a Dictionary of dictionaries
            Backs up self.collection before clearing it. Restores the data if there was a problem reading JSON File

            :raises Exception: If there is a problem with the restore
            """
        saved_data = self.collection.copy()  # make a backup copy of data

        try:
            self.collection = super().restore(self._filename)
        except Exception:
            self.collection = saved_data  # On error, restores data
            raise Exception('JsonIO() unable to restore from file')

    def save(self):
        """ Calls JsonIO.save() method which in turns calls self._make_json_dict before writing the file"""

        super().save(self._filename)

    def add(self, obj_uid, obj):
        """ Adds an object to self.collection
        :param obj: cls: The object to be added
        :param obj_uid: str: The unique id for the object
        :raises Exception: If there is a duplicate obj_id key"""

        if obj_uid in self.collection:
            raise Exception("Duplicate primary_id for object")
        else:
            self.collection[obj_uid] = obj

    def search(self, obj_uid):
        """ Method to find an object in self.collection
        :param obj_uid: str :  The unique id for the object to be found
        :returns the object with obj_id from self.collections. """

        if obj_uid in self.collection:
            return self.collection[obj_uid]
        else:
            raise Exception(f'Invalid key: {obj_uid} does not exist')
