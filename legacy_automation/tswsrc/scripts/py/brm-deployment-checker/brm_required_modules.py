
import os
import io
import sys
import re
import time
import logging
import paramiko

IS_PY3 = sys.version_info[0] == 3


class IllegalArgumentException(Exception):

    def __init__(self, lineno, msg):
        self.lineno = lineno
        self.msg = msg

    def __str__(self):
        s='Exception at line number %d => %s' % (self.lineno, self.msg)
        return s


class Properties(object):
    """
    A Python replacement for java.util.Properties class
    This is modelled as closely as possible to the Java original.

    Created - Anand B Pillai <abpillai@gmail.com>
    """

    def __init__(self, props=None):

        # Note: We don't take a default properties object
        # as argument yet

        # Dictionary of properties.
        self._props = {}
        # Dictionary of properties with 'pristine' keys
        # This is used for dumping the properties to a file
        # using the 'store' method
        self._origprops = {}
        self._keyorder = []
        # Dictionary mapping keys from property
        # dictionary to pristine dictionary
        self._keymap = {}

        self.othercharre = re.compile(r'(?<!\\)(\s*\=)|(?<!\\)(\s*\:)')
        self.othercharre2 = re.compile(r'(\s*\=)|(\s*\:)')
        self.bspacere = re.compile(r'\\(?!\s$)')
        if props:
            self.update(props)

    def __str__(self):
        s='{'
        for key,value in list(self._props.items()):
            s = ''.join((s,key,'=',value,', '))

        s=''.join((s[:-2],'}'))
        return s

    def __parse(self, lines):
        """ Parse a list of lines and create
        an internal property dictionary """

        # Every line in the file must consist of either a comment
        # or a key-value pair. A key-value pair is a line consisting
        # of a key which is a combination of non-white space characters
        # The separator character between key-value pairs is a '=',
        # ':' or a whitespace character not including the newline.
        # If the '=' or ':' characters are found, in the line, even
        # keys containing whitespace chars are allowed.

        # A line with only a key according to the rules above is also
        # fine. In such case, the value is considered as the empty string.
        # In order to include characters '=' or ':' in a key or value,
        # they have to be properly escaped using the backslash character.

        # Some examples of valid key-value pairs:
        #
        # key     value
        # key=value
        # key:value
        # key     value1,value2,value3
        # key     value1,value2,value3 \
        #         value4, value5
        # key
        # This key= this value
        # key = value1 value2 value3

        # Any line that starts with a '#' or '!' is considerered a comment
        # and skipped. Also any trailing or preceding whitespaces
        # are removed from the key/value.

        # This is a line parser. It parses the
        # contents like by line.

        lineno=0
        i = iter(lines)

        for line in i:
            lineno += 1
            line = line.strip()
            # Skip null lines
            if not line: continue
            # Skip lines which are comments
            if line[0] in ('#','!'): continue
            # Some flags
            escaped=False
            # Position of first separation char
            sepidx = -1
            # A flag for performing wspace re check
            flag = 0
            # Check for valid space separation
            # First obtain the max index to which we
            # can search.
            m = self.othercharre.search(line)
            if m:
                first, last = m.span()
                start, end = 0, first
                flag = 1
                wspacere = re.compile(r'(?<![\\\=\:])(\s)')
            else:
                if self.othercharre2.search(line):
                    # Check if either '=' or ':' is present
                    # in the line. If they are then it means
                    # they are preceded by a backslash.

                    # This means, we need to modify the
                    # wspacere a bit, not to look for
                    # : or = characters.
                    wspacere = re.compile(r'(?<![\\])(\s)')
                start, end = 0, len(line)

            m2 = wspacere.search(line, start, end)
            if m2:
                # print 'Space match=>',line
                # Means we need to split by space.
                first, last = m2.span()
                sepidx = first
            elif m:
                # print 'Other match=>',line
                # No matching wspace char found, need
                # to split by either '=' or ':'
                first, last = m.span()
                sepidx = last - 1
                # print line[sepidx]


            # If the last character is a backslash
            # it has to be preceded by a space in which
            # case the next line is read as part of the
            # same property
            while line[-1] == '\\':
                # Read next line
                nextline = next(i)
                nextline = nextline.strip()
                lineno += 1
                # This line will become part of the value
                line = line[:-1] + nextline

            # Now split to key,value according to separation char
            if sepidx != -1:
                key, value = line[:sepidx], line[sepidx+1:]
            else:
                key,value = line,''
            self._keyorder.append(key)
            self.processPair(key, value)

    def processPair(self, key, value):
        """ Process a (key, value) pair """

        oldkey = key
        oldvalue = value

        # Create key intelligently
        keyparts = self.bspacere.split(key)
        # print keyparts

        strippable = False
        lastpart = keyparts[-1]

        if lastpart.find('\\ ') != -1:
            keyparts[-1] = lastpart.replace('\\','')

        # If no backspace is found at the end, but empty
        # space is found, strip it
        elif lastpart and lastpart[-1] == ' ':
            strippable = True

        key = ''.join(keyparts)
        if strippable:
            key = key.strip()
            oldkey = oldkey.strip()

        oldvalue = self.unescape(oldvalue)
        value = self.unescape(value)

        # Patch from N B @ ActiveState
        curlies = re.compile("{.+?}")
        found = curlies.findall(value)

        for f in found:
            srcKey = f[1:-1]
            if srcKey in self._props:
                value = value.replace(f, self._props[srcKey], 1)

        self._props[key] = value.strip()

        # Check if an entry exists in pristine keys
        if key in self._keymap:
            oldkey = self._keymap.get(key)
            self._origprops[oldkey] = oldvalue.strip()
        else:
            self._origprops[oldkey] = oldvalue.strip()
            # Store entry in keymap
            self._keymap[key] = oldkey

        if key not in self._keyorder:
            self._keyorder.append(key)

    def escape(self, value):

        # Java escapes the '=' and ':' in the value
        # string with backslashes in the store method.
        # So let us do the same.
        newvalue = value.replace(':','\:')
        newvalue = newvalue.replace('=','\=')

        return newvalue

    def unescape(self, value):

        # Reverse of escape
        newvalue = value.replace('\:',':')
        newvalue = newvalue.replace('\=','=')

        return newvalue

    def load(self, stream):
        """ Load properties from an open file stream """

        # For the time being only accept file input streams
        if not _is_file(stream):
            raise TypeError('Argument should be a file object!')
        # Check for the opened mode
        if stream.mode != 'r':
            raise ValueError('Stream should be opened in read-only mode!')

        try:
            lines = stream.readlines()
            self.__parse(lines)
        except IOError:
            raise

    def getProperty(self, key):
        """ Return a property for the given key """

        return self._props.get(key,'')

    def setProperty(self, key, value):
        """ Set the property for the given key """

        if type(key) is str and type(value) is str:
            self.processPair(key, value)
        else:
            raise TypeError('both key and value should be strings!')

    def propertyNames(self):
        """ Return an iterator over all the keys of the property
        dictionary, i.e the names of the properties """

        return list(self._props.keys())

    def list(self, out=sys.stdout):
        """ Prints a listing of the properties to the
        stream 'out' which defaults to the standard output """

        out.write('-- listing properties --\n')
        for key,value in list(self._props.items()):
            out.write(''.join((key,'=',value,'\n')))

    def store(self, out, header=""):
        """ Write the properties list to the stream 'out' along
        with the optional 'header' """

        if out.mode[0] != 'w':
            raise ValueError('Steam should be opened in write mode!')

        try:
            out.write(''.join(('#',header,'\n')))
            # Write timestamp
            tstamp = time.strftime('%a %b %d %H:%M:%S %Z %Y', time.localtime())
            out.write(''.join(('#',tstamp,'\n')))
            # Write properties from the pristine dictionary
            for prop in self._keyorder:
            # changed _origprops to _props in next line. Why so?
                if prop in self._props:
                    val = self._origprops[prop]
                    out.write(''.join((prop,'=',self.escape(val),'\n')))

            out.close()
        except IOError:
            raise

    def getPropertyDict(self):
        return self._props

    def deleteProperty(self, name):
        """ Delete the property
        :param name: key name
        :return:
        """
        del self._props[name]
        del self._origprops[name]
        self._keyorder.remove(name)

    def update(self, kv_dict):
        """ Updates the properties with entries in kv_dict

        :param kv_dict: dictionary
        :return:
        """
        if not isinstance(kv_dict, dict):
            raise TypeError("kv_dict must be a dict! found:" % kv_dict)
        for key in kv_dict:
            self.setProperty(key, kv_dict[key])

    def write_to_file(self, file_name):
        """
        Write to a text file name
        :param file_name: File name
        :return:
        """
        with open(file_name, 'w') as fpw:
            self.store(fpw)

    def __getitem__(self, name):
        """ To support direct dictionary like access """

        return self.getProperty(name)

    def __setitem__(self, name, value):
        """ To support direct dictionary like access """

        self.setProperty(name, value)

    def __getattr__(self, name):
        """ For attributes not found in self, redirect
        to the properties dictionary """

        try:
            return self.__dict__[name]
        except KeyError:
            if hasattr(self._props,name):
                return getattr(self._props, name)

    def __delitem__(self, name):
        self.deleteProperty(name)


def _is_file(obj):
    return isinstance(obj, io.IOBase)


class SSHConnection(object):
    """Connects and logs into the specified hostname.
    Arguments that are not given are guessed from the environment."""

    def __init__(self,
                 host,
                 username=None,
                 private_key=None,
                 password=None,
                 port=22):
        self.host = host
        self.username = username
        log_msg = 'SSHConnection: host: %s ' % host \
                  + 'username: %s ' % username \
                  + 'private_key: %s ' % private_key \
                  + 'password: %s ' % password \
                  + 'port: %s' % str(port)
        logging.debug('HOST :- %s' % self.host + log_msg)
        self._sftp_live = False
        self._sftp = None
        if not username:
            raise TypeError("You have not specified a username")

        # Begin the SSH transport.
        self._transport = paramiko.Transport((host, port))
        self._transport_live = True
        # Authenticate the transport.
        if password:
            # Using Password.
            self._transport.connect(username=username, password=password)
        else:
            # Use Private Key.
            if not private_key:
                raise TypeError("You have not specified a password or key.")
            private_key_file = os.path.expanduser(private_key)
            if not os.path.isfile(private_key_file):
                raise KeyError('SSH Key not found! %s' % private_key_file)
            rsa_key = paramiko.RSAKey.from_private_key_file(private_key_file)
            self._transport.connect(username=username, pkey=rsa_key)

    def _sftp_connect(self):
        """Establish the SFTP connection."""
        if not self._sftp_live:
            self._sftp = paramiko.SFTPClient.from_transport(self._transport)
            self._sftp_live = True

    def execute(self, command):
        """Execute the given commands on a remote machine."""
        channel = self._transport.open_session()
        self._transport.set_keepalive(30)
        logging.info('HOST %s:- ' % self.host + 'EXEC: %s', command)
        channel.exec_command('source .bash_profile;' + command)
        sout = channel.makefile('rb', -1).readlines()
        # output = [x.strip() for x in output]
        # output = [x.strip() for x in output]
        serr = channel.makefile_stderr('rb', -1).readlines()
        # todo: write the files to current directory, just like ShellExecutor
        stdout_str = b''.join(sout).decode('UTF-8')
        stderr_str = b''.join(serr).decode('UTF-8')
        logging.debug('HOST %s:- ' % self.host + 'Stdout: %s\nStderr: %s', stdout_str, stderr_str)
        return stdout_str, stderr_str

    def close(self):
        """Closes the connection and cleans up."""
        # Close SFTP Connection.
        if self._sftp_live:
            self._sftp.close()
            self._sftp_live = False
            # Close the SSH Transport.
        if self._transport_live:
            self._transport.close()
            self._transport_live = False

    def get_rpm_list(self, grep_prefix=""):
        """Greps list of installed rpm packages based on grep prefix"""
        rpms = []
        if not grep_prefix.startswith('^'):
            grep_prefix = '^' + grep_prefix
        stdoe = self.execute('rpm -qa | grep "%s"' % grep_prefix)
        pkgs = stdoe[0].splitlines()
        for pkg in pkgs:
            if str(pkg).strip() != '':
                rpms.append(str(pkg).strip())
        return rpms
