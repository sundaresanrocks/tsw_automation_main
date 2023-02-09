#!/usr/bin/python
"""unit test for sequence_generator.py"""

#    sequence_generator_test.py - Unit tests fro sequence_generator.py
#    Copyright (C) 2010  Scott Carpenter (scottc@movingtofreedom.org)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
import os
import sys
from io import StringIO
from zlib import crc32
import libx.sequence_generator as sequence_generator

LOTS_OF_VALUES = 10000

# Redirector from Mark Pilgrim, "Dive Into Python"
class Redirector(unittest.TestCase):
    def setUp(self):
        self.savestdout = sys.stdout
        self.redirect = StringIO()
        sys.stdout = self.redirect

    def tearDown(self):
        sys.stdout = self.savestdout

class BasicSequences(unittest.TestCase):

    def test_numbers_and_letters(self):
        """base numbers and letters"""
        self.assertEqual(sequence_generator.SeqGen.NUMBERS, '0123456789')
        self.assertEqual(sequence_generator.SeqGen.LETTERS,
                         'abcdefghijklmnopqrstuvwxyz')

    def test_default_sequence(self):
        """default (ALPHANUM_36) sequence"""
        seq = sequence_generator.SeqGen()
        values = ''
        for i in range(40):
            values += next(seq)
        self.assertEqual(values, seq.NUMBERS[1:] + seq.LETTERS + '1011121314')

    def test_numbers_sequence(self):
        """NUMBERS sequence"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.NUMBERS)
        values = []
        values_py = []
        for i in range(1, LOTS_OF_VALUES):
            values.append(next(seq))
            values_py.append(str(i))
        self.assertEqual(values, values_py, 'difference in %s values generated'
                         ' by SeqGen and Python range' % LOTS_OF_VALUES)

    def test_letters_sequence(self):
        """LETTERS sequence"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.LETTERS)
        values = ''
        for i in range(30):
            values += next(seq)
        self.assertEqual(values, seq.LETTERS[1:] + 'babbbcbdbe')

    def test_hex_sequence(self):
        """HEX sequence"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.HEX)
        values = []
        values_py = []
        for i in range(1, LOTS_OF_VALUES):
            values.append(next(seq))
            values_py.append(str(hex(i))[2:])
        self.assertEqual(values, values_py, 'difference in %d values generated'
                         ' by SeqGen and Python range+hex' % LOTS_OF_VALUES)

    def test_alphanum_36_sequence(self):
        """ALPHANUM_36 sequence"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.ALPHANUM_36)
        values = ''
        for i in range(40):
            values += next(seq)
        self.assertEqual(values, seq.NUMBERS[1:] + seq.LETTERS + '1011121314')

    def test_alphanum_62_sequence(self):
        """ALPHANUM_62 sequence"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.ALPHANUM_62)
        values = ''
        for i in range(66):
            values += next(seq)
        self.assertEqual(values, seq.NUMBERS[1:] + seq.LETTERS +
                                 seq.LETTERS.upper() + '1011121314')

    def test_alphanum_26_sequence(self):
        """ALPHANUM_26 sequence"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.ALPHANUM_26)
        values = ''
        for i in range(30):
            values += next(seq)
        self.assertEqual(values, seq.ALPHANUM_26[1:] + '4344454647')
        
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.ALPHANUM_26)
        values = []
        for i in range(1, LOTS_OF_VALUES):
            values.append(next(seq))
        self.assertEqual(crc32(str(values).encode('utf8')), 2477957434)

    def test_bin_sequence(self):
        """binary sequence"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        '01')
        values = []
        values_py = []
        for i in range(1, LOTS_OF_VALUES):
            values.append(next(seq))
            values_py.append(str(bin(i))[2:])
        self.assertEqual(values, values_py, 'difference in %d values generated'
                         ' by SeqGen and Python range+bin' % LOTS_OF_VALUES)
        
class Init(unittest.TestCase):
    
    def test_init(self):
        """__init__ input parameter validation"""
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          'abcdb')
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          'abcdba')
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          '''ab
                          cd''')
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          'ab                cd')
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          'ab\tcd')
        # bad stop value
        self.assertRaises(ValueError,
                          sequence_generator.SeqGen,
                          'abc')
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          'a')
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          'aa')
        self.assertRaises(TypeError,
                          sequence_generator.SeqGen,
                          sequence_generator.SeqGen.NO_STOP,
                          None)

class Value(unittest.TestCase):
    
    def test_get_value(self):
        """get_value"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.LETTERS)
        self.assertEqual(seq.value, 'a')
        self.assertEqual(seq._get_value(), 'a')
        self.assertEqual(seq.value, seq.seqchars[0])
        
    def test_set_value(self):
        """set_value"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.LETTERS)
        seq.value = 'x'
        self.assertEqual(seq.value, 'x')
        seq._set_value('')
        self.assertEqual(seq.value, 'a')
        seq.value = ' '
        self.assertEqual(seq.value, 'a')
        self.assertRaises(sequence_generator.SeqGenInvalidValueError,
                          seq._set_value, '>')
    def test_validate(self):
        """validate"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.HEX)
        self.assertRaises(sequence_generator.SeqGenInvalidValueError,
                          seq.validate, '%')
        
class Rollover(unittest.TestCase):
    def test_rollover(self):
        """rollover"""
        seq = sequence_generator.SeqGen()
        self.assertRaises(ValueError, seq._set_rollover_len, 'a')
        seq.rollover_len = -2
        self.assertEqual(seq.rollover_len, seq.NO_ROLLOVER)
        # normal rollover
        seq.rollover_len = 3
        seq.value = 'zz'
        next(seq)
        self.assertEqual(seq.value, seq.seqchars[1],
                         "didn't rollover as expected")
        seq = sequence_generator.SeqGen()
        # rollover is less than current value
        seq.value = 'wwwwww'
        seq.rollover_len = 4
        self.assertEqual(seq.value, 'wwwwww')
        next(seq)
        self.assertEqual(seq.value, seq.seqchars[1],
                         "didn't rollover as expected after setting rollover "
                         'len to less than current value len')

class SeqChars(unittest.TestCase):
    def test_seqchars(self):
        """seqchars"""
        seq = sequence_generator.SeqGen(sequence_generator.SeqGen.NO_STOP,
                                        sequence_generator.SeqGen.LETTERS)
        self.assertEqual(seq.seqchars, seq.LETTERS)
        self.assertRaises(sequence_generator.SeqGenError,
                          seq._set_seqchars, 'abc')
        
class Iteration(unittest.TestCase):
    def test_iteration(self):
        """iteration / stop iteration"""
        # 0 and 1 should result in no values
        values = []
        for i in sequence_generator.SeqGen(0, sequence_generator.SeqGen.HEX):
            values.append(next(seq))
        self.assertEqual(values, [], 'stoplen of 0 should have no iteration')
        values = []
        for i in sequence_generator.SeqGen(1, sequence_generator.SeqGen.HEX):
            values.append(next(seq))
        self.assertEqual(values, [], 'stoplen of 1 should have no iteration')
        
        values = ''
        for i in sequence_generator.SeqGen(2, sequence_generator.SeqGen.HEX):
            values += i
        self.assertEqual(values, '123456789abcdef',
                         "stoplen of 2 didn't yield expected values")
        
        # rollover len should have no effect
        seq = sequence_generator.SeqGen(2, sequence_generator.SeqGen.HEX)
        seq.rollover_len = 3
        values = ''
        for i in seq:
            values += i
        self.assertEqual(values, '123456789abcdef',
                         "stoplen of 2 and rollover_len of 3 didn't yield "
                         'expected values')
        
        # stoplen should never be reached when rollover_len is less
        seq = sequence_generator.SeqGen(3, '012')
        seq.rollover_len = 2
        values = ''
        count = 0
        for i in seq:
            values += i
            count += 1
            if count > 20: break
        self.assertEqual(values, '121212121212121212121',
                         "stoplen of 3 and rollover_len of 2 didn't yield "
                         'expected values')

class Main(Redirector):
    
    def test_main_good_input(self):
        """main with good input"""
        # no input
        known_result = ('last value = \n'
                        'next value = 1\n')
        sequence_generator.main(['sequence_generator.py'])
        self.assertEqual(self.redirect.getvalue(), known_result)
        
        # # good "last value" and default sequence
        # self.redirect.truncate(0)
        # known_result = ('last value = 1\n'
        #                 'next value = 2\n')
        # sequence_generator.main(['sequence_generator.py', '1'])
        # redirect_val = self.redirect.getvalue().strip()
        # # self.assertEqual(redirect_val, known_result)
        # #
        # # good "last value" and hex sequence
        # self.redirect.truncate(0)
        # known_result = ('last value = ff\n'
        #                 'next value = 100\n')
        # sequence_generator.main(['sequence_generator.py', 'ff',
        #                          '0123456789abcdef'])
        # self.assertEqual(self.redirect.getvalue(), known_result)

    def test_main_bad_input(self):
        """main with bad input"""
        # bad "last value" (not in alphabet)
        self.assertRaises(sequence_generator.SeqGenInvalidValueError,
                          sequence_generator.main,
                          ['sequence_generator.py', '$'])
        # bad alphabet
        self.assertRaises(sequence_generator.SeqGenInvalidAlphabetError,
                          sequence_generator.main,
                          ['sequence_generator.py', '', 'abccba'])

if __name__ == "__main__":
    unittest.main()
