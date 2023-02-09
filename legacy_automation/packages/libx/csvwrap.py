"""
CSV wrap
"""
__author__ = 'Manoj'

import copy
import csv
# import logging
import pprint
import io
import os
# import sys
import logging
from functools import partial
from collections import OrderedDict
from path import Path


def csv_from_excel(excel_file, csv_file_prefix, worksheets):
    """

    :param excel_file: Path to excel file
    :param csv_file_prefix: Prefix for csv file.
    :param worksheets: List of worksheet names
    :return:
    """
    import openpyxl
    import csv

    # input validation
    if isinstance(worksheets, str):
        worksheets = [worksheets]

    # load work book
    work_book = openpyxl.load_workbook(excel_file)
    for work_sheet in worksheets:
        # load work sheet
        sheet = work_book.get_sheet_by_name(work_sheet)
        if not sheet:
            raise Exception('Empty work sheet. %s' % locals())
        # write to csv file
        #todo: use io.StringIO() here... use option to create temp files...
        with open(csv_file_prefix + work_sheet + '.csv', 'w', encoding='utf-8', newline='') as csv_fh:
            csv_writer = csv.writer(csv_fh, quoting=csv.QUOTE_ALL)
            for row in sheet.rows:
                csv_writer.writerow([cell.value if cell.value else '' for cell in row])


def _pointer_bool(in_str):
    """
    Boolean typecast function
    :param in_str: Input string or unicode
    :return: boolean
    """
    if not in_str or not in_str.strip():
        return False
    if in_str.lower() == 'true':
        return True
    return False


def _pointer_list(in_str, delimiter=","):
    """
    Typecasts a string into a list based on delimiter
    :param in_str: Input string or unicode
    :param delimiter: used in split call
    :return: a list of string or unicode
    """
    if not in_str or not in_str.strip():
        return []
    return in_str.split(delimiter)


class TypeCastDefinition:
    """
    Class to define the different type casts that can be used for parsing csv file
    """

    def __init__(self):
        self._supported_types = {}
        self.add_type("bool", _pointer_bool)
        self.add_type("list", _pointer_list)

    def get_supported_types(self):
        """
        The list of supported types
        :return: List of supported types
        """
        return iter(list(self._supported_types.keys()))

    def add_type(self, type_name, type_method):
        """
        Adds a new supported type
        :param type_name: A named string to identify the data type. Will replace the supported types.
        :param type_method: A callable function. Will take one argument and must return converted type
        :return: True on success
        """
        if not(type(type_name) == str):
            raise TypeError('type_name must be str or unicode')
        if not str(type(type_method).__name__) == 'function':
            raise TypeError('type_method is not callable')
        self._supported_types[type_name] = type_method

    def typecast(self, type_name, input_data):
        """
        Type casts a given type
        :param input_data: The input to be type casted
        :param type_name: Valid type_name
        :return: type casted object
        """
        if not(type(type_name) == str):
            raise TypeError('type_name must be str or unicode')
        if type_name not in self.get_supported_types():
            raise ValueError("type_name: %s is not supported" % type_name)
        func = partial(self._supported_types[type_name], input_data)
        return func.__call__()


def load_csv_as_head_and_data_tuple(csv_file):
    """Loads the data from csv file.
    Returns (header),((row 1), (row 2)...(row n))
    Raises IndexError when number of rows is less than or equal to one.
    :rtype : list of tuples
    :param csv_file: path to the csv file
    """
    ## check if file exists
    if not os.path.isfile(csv_file):
        _msg = 'CSV File: %s not found' % csv_file
        logging.error(_msg)
        raise IOError(_msg)

        ## load the csv file
    lines = []
    with open(csv_file, newline='', encoding='utf-8') as fr:
        reader = csv.reader(fr)
        [lines.append(line) for line in reader if len(line) != 0]

        ## error out if less then 2 rows including header
    if len(lines) < 2:
        raise IndexError('No Header/data rows in csv. Count: %s' % len(lines))
    head = lines.pop(0)
    return tuple(head), tuple(lines)


def group_by(data_list, column_name):
    # Group by the first column
    data_dict = OrderedDict({})
    for dict_row in data_list:
        new_row = copy.deepcopy(dict_row)
        column_value = new_row.pop(column_name)
        if column_value in data_dict:
            data_dict[column_value].append(new_row)
        else:
            data_dict[column_value] = [new_row]
    return data_dict


def load_and_parse_csv_as_dict(csv_file, column_list=None, group_by_list=None, unique_list=None,
                               typecast_map=None, custom_typecast_object=None):
    """
    Loads a csv, does basic checks and tries to parse it as a dict
    :param csv_file: path to csv file
    :param column_list: list of mandatory columns in csv file
    :param group_by_list: collage by the key in order
    :param unique_list: The entries in this column must be unique, not null
    :param typecast_map: A dict with columns as keys that can be used in typecast
    :param custom_typecast_object: An object of TypeCastDefinition that can be used in typecast
    :return: dict
    :raises IndexError if no header/data rows in csv file
    :raises IndexError if no header/data rows in csv file
    """
    if not column_list:
        column_list = []
    if not group_by_list:
        group_by_list = []
    if not unique_list:
        unique_list = []
    if typecast_map:
        if not isinstance(typecast_map, dict):
            raise TypeError("typecast_map must be dict")
        if not custom_typecast_object:
            custom_typecast_object = TypeCastDefinition()
        if not isinstance(custom_typecast_object, TypeCastDefinition):
            raise TypeError("custom_typecast_object must be an instance of TypeCastDefinition")
    else:
        typecast_map = {}

    head_row, data_rows = load_csv_as_head_and_data_tuple(csv_file)
    assert isinstance(data_rows, tuple)

    # Check input
    if isinstance(column_list, str):
        column_list = [column_list]
    if isinstance(group_by_list, str):
        group_by_list = [group_by_list]
    if not (isinstance(column_list, tuple) or isinstance(column_list, list)):
        raise TypeError('column_list must be list or tuple. Found: %s' % type(column_list))
    if not (isinstance(group_by_list, tuple) or isinstance(group_by_list, list)):
        raise TypeError('group_by must be list or tuple. Found: %s' % type(group_by_list))

    # Check relationship between group_by and column_list
    cols_not_found = [col for col in group_by_list if col not in column_list]
    if cols_not_found:
        raise KeyError('NotInColumnList: %s' % cols_not_found + 'All group_by columns must be in column_list')

    # Check relationship between typecast_map and column_list
    cols_not_found = [col for col in typecast_map if col not in column_list]
    if cols_not_found:
        raise KeyError('NotInColumnList: %s' % cols_not_found + 'All typecast_map columns must be in column_list')

    # Process head row - check for duplicate and required columns
    if len(set(column_list)) != len(column_list):
        raise KeyError('DuplicateColumn: %s' % column_list)
    cols_not_found = [col for col in column_list if col not in head_row]
    if cols_not_found:
        raise KeyError('MissingColumn: %s' % cols_not_found)

    # Map the column names to corresponding index
    header = {}
    for index, key in enumerate(head_row):
        header[key] = index

    # Type cast checks based on typecast_map
    typecast_errors = []
    for col in typecast_map:
        if typecast_map[col] not in custom_typecast_object.get_supported_types():
            typecast_errors.append(col)
    if typecast_errors:
        raise ValueError("Following typecast_names not found: %s" % typecast_errors)

    # Typecast the data in each row based on typecast_map
    for row in data_rows:
        for col in typecast_map:
            row[header[col]] = custom_typecast_object.typecast(typecast_map[col], row[header[col]])

    # Data for group_by should not be empty
    _errs_no_data, _errs_duplicate = [], []
    _temp_unique_dict = {}
    _msg = None
    for key in unique_list:
        _temp_unique_dict[key] = set()
    for row in data_rows:
        counter = 1
        # Check for missing column data
        for column_name in group_by_list:
            if not row[header[column_name]]:
                _msg = 'Data Row: %s\t\t' % counter + 'Empty data for column: %s\t\t' % column_name + '%s' % \
                       pprint.pformat(row)
                _errs_no_data.append(_msg)

        # Check for duplicate column data
        for column_name in unique_list:
            if row[header[column_name]] in _temp_unique_dict[column_name]:
                _msg = 'Data Row: %s\t\t' % counter + 'Duplicate data for column: %s\t\t' % column_name + '%s' % \
                       pprint.pformat(row)
                _errs_duplicate.append(_msg)
            else:
                _temp_unique_dict[column_name].add(row[header[column_name]])

    # Throw error messages if any
    _msg1, _msg2 = None, None
    if _errs_no_data:
        _msg1 = 'Missing Data:\n%s' % _msg + '\n'.join(_errs_no_data)
    if _errs_duplicate:
        _msg2 = 'Duplicate Data for Unique Fields: ' + '\n'.join(_errs_duplicate)
    if _msg1 or _msg2:
        logging.error("%s\n%s" % (_msg1, _msg2))
        raise ValueError("%s\n%s" % (_msg1, _msg2))

    # Create a skeleton dictionary based on header column names
    empty_row = {k: "" for k in header}

    # Create a list of dict with csv rows
    data_list = []
    for index, data_row in enumerate(data_rows):
        new_row = copy.deepcopy(empty_row)
        for column_name in header:
            new_row[column_name] = data_row[header[column_name]]
        data_list.append(new_row)

    # Return a list of dict if no group_by
    if not group_by_list:
        return data_list

    # group_by is set. Collate the rows based on the group_by term
    logging.warning('HACK: ONLY FIRST ITEM IN GROUP BY IS CONSIDERED. ADD FOR FURTHER ITEMS...')
    if len(group_by_list) > 2:
        raise ValueError('group_by_list can have at max two entries. TODO: Fix in future')
        #TODO: multiple column support for group_by field

    data_dict = group_by(data_list, group_by_list[0])

    if len(group_by_list) == 1:
        return data_dict

    for group_key in data_dict:
        data_dict[group_key] = group_by(data_dict[group_key], group_by_list[1])

    return data_dict


def load_test_data(excel_or_csv, worksheets, column_list='test'.split(','), test_aggregation_column='test',
                   skip_empty_test=True):
    """
    Function to load test data from excel and pass it to test generator
    :param worksheets: List of worksheet names
    :param column_list: Column list that must be present
    :param test_aggregation_column: Column that indentifies a test. Data grouping is based on this field.
    :return: List of dicts
    """
    if isinstance(worksheets, str):
        worksheets = [worksheets]

    # ensure excel_or_csv is of type Path
    excel_or_csv = Path(excel_or_csv)

    input_list = []
    ids_list = []

    def _append_to_return(_csv):
        # parse the csv file into list and dict
        excel_dict = load_and_parse_csv_as_dict(csv_file=_csv,
                                                column_list=column_list,
                                                group_by_list=[test_aggregation_column])
        for test in excel_dict:
            # skip tests with empty test names
            if test == '':
                continue
            ids_list.append(test)
            input_list.append(excel_dict[test])
        #todo: do validation on ids -> ensure that there is no duplicates

    if excel_or_csv.ext in ['.csv']:
        _append_to_return(excel_or_csv)
    elif excel_or_csv.ext in ['.xls', '.xlsx']:
        # save excel as csv file
        csv_file_prefix = excel_or_csv.dirname().joinpath(excel_or_csv.namebase) + '-'
        csv_from_excel(excel_or_csv, csv_file_prefix=csv_file_prefix, worksheets=worksheets)

        for worksheet in worksheets:
            csv_file = csv_file_prefix + worksheet + '.csv'
            if not os.path.isfile(csv_file):
                raise Exception('Unable to create csv file at %s' % csv_file)
            _append_to_return(csv_file)
    else:
        raise TypeError('File extension must be csv or xlsx. found:{}'.format(excel_or_csv.ext))

    return {'argvalues': input_list,
            'ids': ids_list}


if __name__ == "__main__":
    raise NotImplementedError('This module must be imported, not run!')
