"""Classes to enable JSON read and write functionality """

import json
from abc import ABC, abstractmethod


class CustomDecode(json.JSONDecoder):
    """ The standard JSONDecoder has an object hook option to specify a function to decode the data into a specific
    object. However, this does not cope with lists of objects - such as the reservations list.
    This custom JSONDecoder overloads the object hook with a custom function based on the object type.
    When writing the relevant data to JSON format a {class: tag} entry is added to the entry. If 'class' is a field in
    the dictionary, then custom calls are made to create the relevant object from the data depending on class type"""

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.dict_to_obj)

    @staticmethod
    def dict_to_obj(dct):
        from Library import BookItem
        from Loans import LoanItem
        from Membership import Member
        from Reservations import ReservationItem
        obj = dct
        if 'class' in dct.keys():
            if dct['class'] == '__BookItem__':
                obj = BookItem.create(dct)
            if dct['class'] == '__Member__':
                obj = Member.create(dct)
            if dct['class'] == '__LoanItem__':
                obj = LoanItem.create(dct)
            if dct['class'] == '__ReservationItem__':
                obj = ReservationItem.create(dct)
        return obj


class _JsonIO(ABC):
    """ A Mixin class which provides methods to read and write objects to a file
        in json format """
    filename = ''

    @abstractmethod
    def _make_json_dict(self):
        """  The method provides a data structure that is storable in a json file.
        The method is overloaded by child classes as necessary """
        return {}

    def save_to_file(self, file):
        """ Saves the list of dict returned from a class' _make_json_dict method to self._filename in json format.
            :param file: str: the file name to save to without a suffix
            :raises Exception: If the file can not be written """
        file = self.filename
        try:
            with open(file + '.json', mode='w',
                      encoding='utf-8-sig') as JsonFile:
                json.dump(self._make_json_dict(), JsonFile)

        except Exception:
            raise Exception(f'Unable to write to file {file}')

    def restore(self, file):
        """ :param file: str: the file name to save to without a suffix
            :raises Exception: If the data can not be read and restored
            :raises FileNotFound: If the file path is incorrect or the file does not exist
        returns: JsonFileObj: dict: data stored in the JSON file reformed into the correct object types
        JsonFileObj
            If file is empty or does not exist, an exception is raised"""

        try:
            with open(file + '.json', 'r',
                      encoding='utf-8-sig') as JsonFile:
                JsonFileObj = json.load(JsonFile, object_hook=CustomDecode().dict_to_obj)
                return JsonFileObj
        except FileNotFoundError:
            raise FileNotFoundError(f'Unable to find {file}.json')
        except Exception:
            raise Exception('Unable to restore from file {file}')
