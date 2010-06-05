import random
import hashlib
import base64

def generate_key():
    key = hashlib.sha224(str(random.getrandbits(256))).digest()
    key = base64.b64encode(key, 
            random.choice(['rA','aZ','gQ','hH','hG','aR','DD']))
    key = key.rstrip('==')
    return key
