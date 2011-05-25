import unittest2

from nose.tools import ok_

from filters import strip_signatures, strip_quoted

class SignatureStripTest(unittest2.TestCase):
    def setUp(self):
        self.prefix = """This is the message.\nIt is on multiple
                 lines.\n\nFoo.\n"""
        self.postfix = """\nThis is the content after the signature.\nIt should
                not be in the final result.\n"""

    def _check_for_signature(self, signature):
        result = strip_signatures(self.prefix + signature + self.postfix)
        ok_(result.startswith(self.prefix[0:-1]))
        ok_(self.postfix not in result)
        ok_(signature not in result)

    def test_no_signature(self):
        result = strip_signatures(self.prefix + self.postfix)
        ok_(result.startswith(self.prefix))
        ok_(self.postfix in result)

    def test_standard_signature(self):
        self._check_for_signature("-- \n")

    def test_standard_missing_space_signature(self):
        self._check_for_signature("--\n")

    def test_carriage_return(self):
        self._check_for_signature("--\r\n")

    def test_iphone(self):
        self._check_for_signature("Sent from my iPhone")

    def test_blackberry(self):
        self._check_for_signature("Sent from my BlackBerry")

    def test_from_my_anything(self):
        self._check_for_signature("Sent from my super cool phone")


class QuotedStripTest(unittest2.TestCase):
    def setUp(self):
        self.prefix = """This is the message.\nIt is on multiple
                 lines.\n\nFoo.\n"""
        self.postfix = """\nThis is the content after the signature.\nIt should
                not be in the final result.\n"""

    def _check_for_quoted(self, quoted):
        result = strip_quoted(self.prefix + quoted + self.postfix)
        ok_(result.startswith(self.prefix[0:-1]))
        ok_(self.postfix not in result)
        ok_(quoted not in result)
        return result

    def test_outlook(self):
        self._check_for_quoted("-----Original Message-----")

    def test_outlook_alternative(self):
        self._check_for_quoted("________________________________")

    def test_mail_app(self):
        self._check_for_quoted("On Tuesday Sue wrote:\n")

    def test_failsafe(self):
        self._check_for_quoted("From: Bob")

    def test_multiple(self):
        result = self._check_for_quoted("On Tuesday Sue wrote:\n> Something\n")
        ok_("Tuesday" not in result)

    def test_carriage_return(self):
        result = self._check_for_quoted(
                "On Tuesday Sue wrote:\r\n> Something\n")
        ok_("Tuesday" not in result)
