import random
import hashlib
import base64

def generate_key():
    key = hashlib.sha224(str(random.getrandbits(256))).digest()
    key = base64.b64encode(key, 
            random.choice(['rA','aZ','gQ','hH','hG','aR','DD']))
    key = key.rstrip('==').lower()
    return key

def chunked(seq, n):
    """By Ned Batchelder.
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

def find_dict_key(dictionary, search_value):
    for key, value in dictionary.iteritems():
        if value == search_value:
            return key

def extract(dictionary, keys):
    """Returns a new dictionary with only the keys from the dictionary passed in
    specified in the keys list.
    
    """
    return dict((key, dictionary[key]) for key in keys if key in dictionary)

