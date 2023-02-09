#!/usr/bin/python
"""Generate sequence of unique string values using an arbitrary "alphabet"."""

# sequence_generator.py - Generates a sequence of unique values.
# Copyright (C) 2010  Scott Carpenter (scottc@movingtofreedom.org)
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
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys


class SeqGen(object):
    """Iterator class that generates the sequence values."""

    NUMBERS = '0123456789'
    LETTERS = 'abcdefghijklmnopqrstuvwxyz'
    HEX = NUMBERS + LETTERS[:6]
    ALPHANUM_36 = NUMBERS + LETTERS
    ALPHANUM_62 = NUMBERS + LETTERS + LETTERS.upper()
    # drop 0, 1, 2, vowels, L, and Z to avoid any confusion and actual words:
    ALPHANUM_26 = '3456789BCDFGHJKMNPQRSTVWXY'

    NO_ROLLOVER = -1
    NO_STOP = -1

    def __init__(self, stoplen=NO_STOP, seqchars=ALPHANUM_36):
        """Iteration will stop when the length of the next sequence value
        equals stoplen. (-1 = NO_STOP)
        """
        self._seqchars = seqchars

        not_allowed = {'\n', '\r', '\t', ' '}
        if set(self._seqchars) - not_allowed != set(self._seqchars):
            raise SeqGenInvalidAlphabetError('The following characters are '
                                             'not allowed in a sequence generator alphabet: %s' %
                                             list(not_allowed))

        if len(self._seqchars) < 2 or (len(self._seqchars) == 2 and
                                               self._seqchars[0] == self._seqchars[1]):
            raise SeqGenInvalidAlphabetError('The sequence generator '
                                             'alphabet must contain at least two unique characters.')

        # sequences: first char must repeat at end so we can detect digit
        # rollover; can pass in '01', for example; user doesn't have to worry
        # about first char repeating at end
        if self._seqchars[0] != self._seqchars[-1]:
            self._seqchars += self._seqchars[0]
        self._value = self._seqchars[0]
        self._rollover_len = self.NO_ROLLOVER

        try:
            stoplen = int(stoplen)
        except ValueError:
            raise

        if stoplen < -1:
            stoplen = self.NO_ROLLOVER
        self._stoplen = stoplen

        if len(set(self._seqchars)) != len(self._seqchars[:-1]):
            raise SeqGenInvalidAlphabetError('Duplicate characters not '
                                             'allowed in a sequence generator alphabet.')

    def __iter__(self):
        return self

    def _get_value(self):
        """Get the current value of the sequence."""
        return self._value

    def _set_value(self, val):
        self._value = self.validate(val)
        if self._value == '':
            self.value = self._seqchars[0]

    def _get_rollover_len(self):
        """The sequence will reset to "zero" (seqchars[0]) when the length
        of the next sequence value equals rollover_len.
        """
        return self._rollover_len

    def _set_rollover_len(self, L):
        try:
            L = int(L)
        except ValueError:
            raise
        if L < 0:
            L = self.NO_ROLLOVER
        self._rollover_len = L

    def _get_seqchars(self):
        """The sequence "alphabet.\""""
        return self._seqchars[:-1]

    def _set_seqchars(self, dummy):
        raise SeqGenError('seqchars is read-only')

    value = property(_get_value, _set_value)
    rollover_len = property(_get_rollover_len, _set_rollover_len)
    seqchars = property(_get_seqchars, _set_seqchars)

    def __next__(self):
        """Get the next sequence value."""
        last_value = ' ' + self._value  # add space as a backstop
        next_value = ''

        increment = True
        for x in reversed(last_value):  # walk backwards, incrementing as needed
            if x == ' ':  # reached the beginning
                if increment:  # all chars rolled over: grow a digit
                    # create new leftmost "zero" to increment
                    x = self._seqchars[0]
                else:
                    break

            if increment:
                next_seqchars_idx = self._seqchars.find(x) + 1
                this_char = self._seqchars[next_seqchars_idx]
                if next_seqchars_idx + 1 < len(self._seqchars):
                    increment = False  # we're done "rolling"
            else:
                this_char = x

            next_value = this_char + next_value  # build new value right to left
            # print(next_value)

        if -1 < self._stoplen <= len(next_value):
            raise StopIteration
        if -1 < self._rollover_len <= len(next_value):
            next_value = self.seqchars[1]

        self._value = next_value
        return next_value

    def validate(self, val):
        """Verify if a valid value for this sequence generator's alphabet."""
        val = val.strip()
        leftovers = set(val) - set(self._seqchars)
        if leftovers != set():
            raise SeqGenInvalidValueError('%s has characters (%s) that are '
                                          'not in this sequence generator\'s alphabet: %s' %
                                          (val, str(list(leftovers)), self._seqchars[:-1]))
        return val


class SeqGenError(Exception): pass


class SeqGenInvalidValueError(SeqGenError): pass


class SeqGenInvalidAlphabetError(SeqGenError): pass


def main(argv=None):
    # main helps with unit testing / calling from interactive prompt
    # also see: http://www.artima.com/weblogs/viewpost.jsp?thread=4829
    if argv is None:
        argv = sys.argv

    last_value = ''
    seqchars = SeqGen.ALPHANUM_36

    if len(argv) > 1:
        last_value = argv[1].strip()
    if len(argv) > 2:
        seqchars = argv[2].strip()

    seq = SeqGen(SeqGen.NO_STOP, seqchars)
    seq.value = last_value
    print(('last value = %s' % last_value))
    print(('next value = %s' % next(seq)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
