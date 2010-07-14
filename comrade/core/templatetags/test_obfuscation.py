from nose.tools import eq_

from .obfuscation import obfuscate_email

def test_obfuscate_email_clean():
    email = 'larry@larrypeplin.com'
    obfuscated_email = obfuscate_email(email)
    eq_(obfuscated_email, '&#108;&#97;&#114;&#114;&#121;&#0064;&#108;&#97;&#114;&#114;&#121;&#112;&#101;&#112;&#108;&#105;&#110;.&#99;&#111;&#109;')
