import random
import hashlib
import base64

def generate_key():
    key = hashlib.sha224(str(random.getrandbits(256))).digest()
    key = base64.b64encode(key, 
            random.choice(['rA','aZ','gQ','hH','hG','aR','DD']))
    key = key.rstrip('==')
    return key

# By Ned Batchelder.
def chunked(seq, n):
    """
    Yield successive n-sized chunks from seq.

    >>> for group in chunked(range(8), 3):
    ...     print group
    [0, 1, 2]
    [3, 4, 5]
    [6, 7]
    """
    for i in xrange(0, len(seq), n):
        yield seq[i:i+n]

def flatten(lst):
    for elem in lst:
        if hasattr(elem, '__iter__'):
            for e in flatten(elem):
                yield e
        else:
            yield elem
