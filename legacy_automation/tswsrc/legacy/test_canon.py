"""
=============================
Canonicalizer test cases
=============================

IP/URL tests for Canonicalizer

"""
from lib.canon import *
from framework.test import SandboxedTest
import unittest


def setUpModule():
    if not os.path.isfile(SH_CANON_CLIENT):
        raise unittest.SkipTest('UrlCanonClient.sh executable not found at %s' % SH_CANON_CLIENT)


from framework.ddt import testgen_file, tsadriver
@tsadriver
class IP(SandboxedTest):
    """Ip related tests"""
    @testgen_file('tsw/canon/ipv4_class_a_private.txt',
                  'tsw/canon/ipv4_class_b_private.txt',
                  'tsw/canon/ipv4_class_c_private.txt',
                  'tsw/canon/ipv6_private.txt')
    def test_private(self, ip):
        """
        test for private ips
        """
        assert_private_ip(ip)

    @testgen_file('tsw/canon/ip_loopback.txt')
    def test_loopback(self, ip):
        """
        test for loopback ips
        """
        assert_private_ip(ip)

    @testgen_file('tsw/canon/ipv4_class_a_public.txt',
                  'tsw/canon/ipv4_class_b_public.txt',
                  'tsw/canon/ipv4_class_c_public.txt',)
    def test_public(self, ip):
        """
        test for public ips
        """
        assert_valid_url(ip)


    @testgen_file('tsw/canon/ipv4_overflow.txt')
    def test_overflow(self, ip):
        """
        overflow in first 3 octets!
        test for ip overflow
        """
        try:
            res = validate_url(ip)
        except UnrecognizedTLDError as err:
            logging.warning(err.args[0])
        else:
            pos = res[1].find('SDK_canonicalize is')
            if pos != -1:
                pos1 = res[1].find('Site Advisor Tests', pos)
                pos2 = res[1].find(ip, pos, pos1)
                if pos2 == -1:
                    raise TestFailure('URL Overflow')

            raise Exception('Unhandled condition')



@tsadriver
class URL(SandboxedTest):
    """ URL tests """
    @testgen_file('tsw/canon/braces_sq_brackets.txt')
    def test_sqbracets_braces(self, url):
        """URLs with [ ] { } """
        assert_valid_url(url)

    @testgen_file('tsw/canon/encoded_octet_in_path.txt')
    def test_enc_octet_path(self, url):
        """URLs - encoded octets in path"""
        assert_valid_url(url)


    @testgen_file('tsw/canon/escape_sequence_cgi.txt')
    def test_esc_cgi(self, url):
        """URLs - escape sequences in cgi"""
        assert_valid_url(url)

    @testgen_file('tsw/canon/escape_sequence.txt')
    def test_esc_path(self, url):
        """URLs - escape sequences in path"""
        assert_valid_url(url)

    @testgen_file('tsw/canon/hash_percent_double_quote.txt')
    def test_hash_perc_dblquote(self, url):
        """with # % \""""
        assert_valid_url(url)

    @testgen_file('tsw/canon/https.txt')
    def test_https(self, url):
        """https test case"""
        assert_valid_url(url)

    @testgen_file('tsw/canon/safe_chars.txt')
    def test_safe_chars(self, url):
        """URLs - safe characters:    ( $, - , _ , . , + )"""
        assert_valid_url(url)

    @testgen_file('tsw/canon/exploratory.txt')
    def test_exploratory(self, url):
        """Exploratory urls"""
        assert_valid_url(url)

    @testgen_file('tsw/canon/pipe_slash_caret_backquote_tilde.txt')
    def test_pip_caret_slash_bckquote(self, url):
        """characters | \\ ^ ` and ~"""
        assert_valid_url(url)

