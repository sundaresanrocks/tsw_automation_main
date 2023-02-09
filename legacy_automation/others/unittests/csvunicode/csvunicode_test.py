__author__ = 'M'
import pprint
# import random
import unittest


class TestCSV(unittest.TestCase):
    """CSV Unicode related unit tests"""

    def test_import_csv_unicode(self):
        import libx.csvwrap

    def test_csv_file_not_found(self):
        import libx.csvwrap as csvwrap

        with self.assertRaisesRegex(IOError, 'CSV File: res/unknown-file.csv not found'):
            pprint.pprint(csvwrap.load_and_parse_csv_as_dict('res/unknown-file.csv'))

    def test_csv_no_lines(self):
        import libx.csvwrap as csvwrap

        try:
            pprint.pprint(csvwrap.load_and_parse_csv_as_dict('res/no-lines.csv'))
        except IndexError as err:
            if not str(err).startswith('No Header'):
                raise

    def test_csv_one_line(self):
        import libx.csvwrap as csvwrap

        return_value = csvwrap.load_and_parse_csv_as_dict('res/prev_unit_01.csv')
        pprint.pprint(return_value)

    def test_prev_check_fields(self):
        import libx.csvwrap as csvwrap
        from libx.csvwrap import TypeCastDefinition

        expected_head_list = 'url,_id,cl_hash,db_hash,in_alexa,in_dms,in_quantcast,in_sanity,alexa,quantcast'.split(',')
        return_value = csvwrap.load_and_parse_csv_as_dict('res/prev_unit_01.csv',
                                                          column_list=expected_head_list,
                                                          typecast_map={'in_alexa': 'bool',
                                                                        'in_dms': 'bool',
                                                                        'in_quantcast': 'bool',
                                                                        'in_sanity': 'bool',
                                                                        'alexa': 'list',
                                                                        'quantcast': 'list'},
                                                          custom_typecast_object=TypeCastDefinition())
        pprint.pprint(return_value)

    def test_prev_check_fields_invalid_column(self):
        import libx.csvwrap as csvwrap
        from libx.csvwrap import TypeCastDefinition

        expected_head_list = 'url,_id,cl_hash,db_hash,in_alexa,in_dms,in_quantcast,in_sanity,alexa,quantcast'.split(',')
        try:
            return_value = csvwrap.load_and_parse_csv_as_dict('res/prev_unit_01.csv',
                                                              column_list=expected_head_list,
                                                              typecast_map={'in_alex': 'bool'},
                                                              custom_typecast_object=TypeCastDefinition()
            )
        except KeyError as err:
            if 'All typecast_map columns must be in column_list' not in str(err):
                raise

    def test_prev_check_fields_valid(self):
        import libx.csvwrap as csvwrap

        expected_head_list = 'test_func,url,Category,Reputation group,error_result,Category Provided By'.split(',')
        return_value = csvwrap.load_and_parse_csv_as_dict('res/end2end_unit_01.csv',
                                                          column_list=expected_head_list,
                                                          group_by_list='test_func',
        )
        pprint.pprint(return_value)


if __name__ == '__main__':
    unittest.main()