__author__ = 'manoj'
import os
import pprint
# import random
import unittest


class TestPyJavaProperties(unittest.TestCase):
    """PyJavaProperties related unit tests"""

    def test_import_py_java_properties(self):
        import libx.pyjavaproperties

    def test_file_not_found(self):
        from libx.pyjavaproperties import Properties
        with self.assertRaisesRegex(IOError, "No such file or directory: 'res/unknown-file.properties'"):
            Properties()

            p = Properties()
            p.load(open('res/unknown-file.properties'))

    def test_load_data(self):
        from libx.pyjavaproperties import Properties
        p = Properties()
        fp = open('res/load-data-file.properties')
        p.load(fp)
        fp.close()
        self.assertEqual(p['one'], '1', 'error while loading data')
        self.assertEqual(p['str'], 'string', 'error while loading data')
        self.assertEqual(p['null'], '', 'error while loading data')

        print(p['one'])
        print(p['str'])
        print(p['null'])

    def test_edit_data(self):
        from libx.pyjavaproperties import Properties
        p = Properties()
        fp = open('res/load-data-file.properties')
        p.load(fp)
        fp.close()
        p['null'] = 'null string'
        temp_file = 'temp.properties'
        if os.path.isfile(temp_file):
            os.unlink(temp_file)
        with open(temp_file, 'w') as fpw:
            p.store(fpw)

        pt = Properties()
        fp = open(temp_file)
        pt.load(fp)
        fp.close()
        self.assertEqual(pt['null'], 'null string', 'Edited value mismatches in new file')
        pt = None

        os.unlink(temp_file)

    def test_delete_keys(self):
        from libx.pyjavaproperties import Properties
        p = Properties()
        fp = open('res/load-data-file.properties')
        p.load(fp)
        fp.close()
        p['null'] = 'null string'
        del p['null']
        temp_file = 'temp.properties'
        if os.path.isfile(temp_file):
            os.unlink(temp_file)
        with open(temp_file, 'w') as fpw:
            p.store(fpw)

        pt = Properties()
        fp = open(temp_file)
        pt.load(fp)
        fp.close()
        print(pt['null'])
        self.assertEqual(pt['null'], '', 'Edited value mismatches in new file')
        pt = None

        os.unlink(temp_file)

    def test_new_key(self):
        from libx.pyjavaproperties import Properties
        p = Properties()
        fp = open('res/load-data-file.properties')
        p.load(fp)
        fp.close()

        p['new-key'] = 'new value'
        temp_file = 'temp.properties'
        if os.path.isfile(temp_file):
            os.unlink(temp_file)
        with open(temp_file, 'w') as fpw:
            p.store(fpw)

        pt = Properties()
        fp = open(temp_file)
        pt.load(fp)
        fp.close()
        print(pt['null'])
        self.assertEqual(pt['new-key'], 'new value', 'new value for new key not found in new file')
        pt = None

        os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()