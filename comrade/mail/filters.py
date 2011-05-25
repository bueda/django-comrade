import re

# Inspired by
# http://stackoverflow.com/questions/1372694/strip-signatures-and-replies-from-emails/2193937#2193937
EMAIL_SIGNATURES = (
        # standard
        re.compile(r'^-- \r*\n$', flags=re.MULTILINE),
        # standard missing space
        re.compile(r'^--\r*\n$', flags=re.MULTILINE),
        # ego-booster
        re.compile(r'^Sent from my', flags=re.MULTILINE),
)

def strip_signatures(body):
    for signature in EMAIL_SIGNATURES:
        split_signature = signature.split(body)
        if len(split_signature) > 1:
            return split_signature[0].strip()
    return body

EMAIL_QUOTED_MARKERS = (
        # outlook
        re.compile(r'^-----Original Message-----', flags=re.MULTILINE),
        # outlook alternative
        re.compile(r'^________________________________', flags=re.MULTILINE),
        # mail.app
        re.compile(r'^On .+wrote:\r*\n', flags=re.MULTILINE),
        # failsafe
        re.compile(r'^From: ', flags=re.MULTILINE),
        # indented
        re.compile(r'^>.*$', flags=re.MULTILINE),
)

def strip_quoted(body):
    for quoted in EMAIL_QUOTED_MARKERS:
        split_message = quoted.split(body)
        if len(split_message) > 1:
            return split_message[0].strip()
    return body
