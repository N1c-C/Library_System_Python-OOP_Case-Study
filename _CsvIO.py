"""Class to provide read functionality with the provided csv files."""

import csv


class _CsvIO:
    """Mixin class to provide a static method to read from a CSV file.
    The class is not intended to be instantiated on its own, hence there is no constructor method"""

    @staticmethod
    def read_csv(filename, **kwargs):
        """
        :param filename : str: name of a csv file - filename should include path
        if the file is not in current dictionary.

        Optional kwargs:
        :param 'Fields': List of str:  A list of column names for the csv values.
        :param 'Start_line': int:  The first line of csv to start reading the data from

        The newline indicator is set as '' and the encoding is set as  'utf-8-sig'

        :raises Exception: When invalid arguments are passed
        :raises FileNotFound: If the CSV filename/path is incorrect or does not exist

        :returns:  a list of dictionaries (each relating to a row in the csv)."""

        if len(kwargs) > 2 or (len(kwargs) == 2
                               and ('Start_line' not in kwargs or 'Fields' not in kwargs)):
            raise Exception("Invalid  key arguments ")

        # sets the starting line in csv to be returned (uses index slicing)
        # Allows first line to be skipped if not using for keys
        start_line = int(kwargs['Start_line']) if 'Start_line' in kwargs else 0

        try:

            with open(filename,
                      mode='r', newline='', encoding='utf-8-sig') as file:

                try:
                    CsvFile = csv.DictReader(file, fieldnames=kwargs['Fields'] if 'Fields' in kwargs else None)

                    return [line for line in CsvFile][start_line:]

                except Exception:  # Exception handling for invalid arguments
                    raise Exception('Invalid arguments')

                    # Exception handling for missing file
        except FileNotFoundError as file_err:
            print(f'There is no such file {file_err.filename}')

        return
