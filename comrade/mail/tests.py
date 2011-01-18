import unittest2

from nose.tools import ok_

from comrade.mail.mail import strip_signatures

class SignatureStripTest(unittest2.TestCase):
    def setUp(self):
        self.prefix = """This is the message.\nIt is on multiple
                 lines.\n\nFoo.\n"""
        self.postfix = """\nThis is the content after the signature.\nIt should
                not be in the final result.\n"""

    def _check_for_signature(self, signature):
        result = strip_signatures(self.prefix + signature + self.postfix)
        ok_(result.startswith(self.prefix))
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

    def test_outlook(self):
        self._check_for_signature("-----Original Message-----")

    def test_outlook_alternative(self):
        self._check_for_signature("________________________________")

    def test_mail_app(self):
        self._check_for_signature("On Tuesday Sue wrote:\n")

    def test_failsafe(self):
        self._check_for_signature("From: Bob")

    def test_iphone(self):
        self._check_for_signature("Sent from my iPhone")

    def test_blackberry(self):
        self._check_for_signature("Sent from my BlackBerry")

    def test_from_my_anything(self):
        self._check_for_signature("Sent from my super cool phone")
